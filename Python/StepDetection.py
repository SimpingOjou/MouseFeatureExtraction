# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 23:19:00 2024

@author: simone
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from copy import deepcopy

import DataManagement as Data

#plt.rcParams["text.usetex"] = True

class Steps:
    def __init__(self, td_data:Data.TrackingData, sampling:int = 199, min_peak_dist:int = 15, peak_prom:int = (0.65, None),\
                flip:bool = False, peak_range:int = 10, lower_quartile:int = 20, upper_quartile:int = 80):
        self.td_data = deepcopy(td_data)
        self.sampling = sampling
        self.figure_number = 0

        self._find_borders(min_peak_dist, peak_prom, flip)
        self._cut_halfsteps(min_peak_dist, peak_prom, flip)
        self._find_peaks(min_peak_dist, peak_prom, not flip)
        self._find_touchdowns()
        self._find_swings(lower_quartile, upper_quartile, peak_range)

    # Finding the borders
    def _find_borders(self, dist:int = 15, prom:int = (0.65, None), flip:bool = False):  
        if flip:
            self.td_data.reverse_origin()

        # The built in dictionary is too unpredictable
        self.borders_paw, b_paw = find_peaks(self.td_data.data["lHindpaw"].y, distance = dist, prominence = prom)
        self.borders_fin, b_fing = find_peaks(self.td_data.data["lHindfingers"].y, distance = dist, prominence = prom)
    
    # Cut halfsteps by looking at first and last touchdown
    def _cut_halfsteps(self, dist:int = 15, prom:int = (0.65, None), flip:bool = False):
        self.lower_t = min([min(self.borders_fin), min(self.borders_paw)])
        self.upper_t = max([max(self.borders_fin), max(self.borders_paw)])

        self.td_data.cut_step(self.lower_t, self.upper_t)
        self.td_data.cut_time(self.lower_t, self.upper_t, self.sampling)

        self._find_borders(dist, prom, flip)

        self.borders_paw = np.insert(self.borders_paw, 0, 0)
        self.borders_paw = np.append(self.borders_paw, len(self.td_data.data["lHindpaw"].y) - 1)
        self.borders_fin = np.insert(self.borders_fin, 0, 0)
        self.borders_fin = np.append(self.borders_fin, len(self.td_data.data["lHindfingers"].y) - 1)

    # Finding the peaks
    def _find_peaks(self, dist:int = 15, prom:int = (0.65, None), flip:bool = False):
        if flip:
            self.td_data.reverse_origin()

        self.peaks_paw, p_paw = find_peaks(self.td_data.data["lHindpaw"].y, distance = dist, prominence = prom) 
        self.peaks_fin, p_fing = find_peaks(self.td_data.data["lHindfingers"].y, distance = dist, prominence = prom)
    
    # Returns the velocities for fingers and paws
    def get_velocities(self):
        timesteps = self.td_data.get_timesteps(self.sampling)
        v_fing = np.diff(self.td_data.data["lHindfingers"].y) / np.diff(timesteps)
        v_paw = np.diff(self.td_data.data["lHindpaw"].y) / np.diff(timesteps)

        return v_fing, v_paw
    
    # Touchdown detection by looking at the borders
    def _find_touchdowns(self):
        self.touchdowns = []

        for i in range(len(self.borders_fin)):
            if self.borders_fin[i] < self.borders_paw[i]:
                self.touchdowns.append(self.borders_fin[i])
            else:
                self.touchdowns.append(self.borders_paw[i])

    # Swing detection with velocity, outliers, and paw condition
    def _find_swings(self, lower:int = 20, upper:int = 80, check_range:int=10):
        self.swings = []
        steps = self.get_steps()
        v_fing, v_paw = self.get_velocities()

        for i,td in enumerate(self.touchdowns[:-1]):
            outliers = self._search_outliers(v_fing, lower, upper)
            # step_mean = np.mean(np.abs(v_fing[td:td+steps[i]])) not used bc percentiles work better
            for j in range(steps[i]):
                if v_fing[td+j] in outliers and self._check_before_peaks(td+j, self.peaks_paw[i], check_range):
                    self.swings.append(td+j)
                    break
    
    # Returns the positions of the steps based on touchdowns
    def get_steps(self):
        return np.diff(self.touchdowns)
    
    def get_step_times(self):
        return [(step + self.lower_t)/self.sampling for step in self.get_steps()]

    def get_swing_times(self):
        return [ (swing + self.lower_t)/self.sampling for swing in self.swings]

    def get_touchdown_times(self):
        return [ (td + self.lower_t)/self.sampling for td in self.touchdowns]

    # Returns true if index i is distant a check_range interval from peaks 
    def _check_before_peaks(self, i:int, peak, check_range:int=10):
        if i + check_range > peak and i < peak:
            return True
        else:
            return False
    
    # Calculates outliers based on lower and upper percentiles
    def _search_outliers(self, data, lower:int = 20, upper:int = 80):
        # Calculate the quartiles (a-th and b-th percentiles)
        q_low, q_up = np.percentile(data, lower), np.percentile(data, upper)
        # Calculate the interquartile range (IQR)
        iqr = q_up - q_low

        # Calculate the lower and upper bounds for outliers
        lower_bound = q_low - 1.5 * iqr
        upper_bound = q_up + 1.5 * iqr

        return [x for x in data if x < lower_bound or x > upper_bound]
    
    def plot_velocities(self, lock_plot:bool = False):
        plt.figure(self.figure_number)
        self.figure_number += 1

        v_fing, v_paw = self.get_velocities()

        plt.plot(v_paw, label = r'$v_{paw}^L$')
        plt.plot(v_fing, label = r"$v_{fin}^L$")
        plt.title("Velocity analysis")
        plt.xlabel("Frames")
        plt.ylabel("Height [cm]")
        plt.grid()
        plt.legend()
        plt.show(block=lock_plot)

    def plot_trajectory(self, lock_plot:bool = False):
        plt.figure(self.figure_number)
        self.figure_number += 1

        plt.plot(self.td_data.data["lHindpaw"].y, label = "L hindpaw")
        plt.plot(self.td_data.data["lHindfingers"].y, label = "L hindfingers")
        plt.plot(self.swings, self.td_data.data["lHindpaw"].y[self.swings], "r^")
        plt.plot(self.swings, self.td_data.data["lHindfingers"].y[self.swings], "r^", label = "swings")
        plt.plot(self.touchdowns, self.td_data.data["lHindfingers"].y[self.touchdowns], "gv")
        plt.plot(self.touchdowns, self.td_data.data["lHindpaw"].y[self.touchdowns], "gv", label = "touchdowns")
        plt.plot(self.peaks_paw, self.td_data.data["lHindpaw"].y[self.peaks_paw], "b*")
        plt.plot(self.peaks_fin, self.td_data.data["lHindfingers"].y[self.peaks_fin], "b*", label = "peaks")
        plt.title("Swings and Touchdown detection")
        plt.xlabel("Frames")
        plt.ylabel("Height [cm]")
        plt.grid()
        plt.legend()
        plt.show()

if __name__=="__main__":
    sampling = 199
    td_sideview = Data.TrackingData(data_name="Side view tracking")
    try:
        # Load the tracking datas
        td_sideview.get_data_from_file(file_path="./Data/Sideview_mouse 35_Run_1.csv")
    except Data.DataFileException as e:
        print(e)
        exit()
    
    s = Steps(td_sideview, sampling)

    s.plot_velocities()
    s.plot_trajectory(lock_plot=True)
