# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 23:19:00 2024

@author: simone
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

import DataManagement as Data
import WorldFrame as WF
import GUI as UI

# def butter_lowpass(cutoff, fs, order=5):
#     nyquist = 0.5 * fs
#     normal_cutoff = cutoff / nyquist
#     b, a = butter(order, normal_cutoff, btype='low', analog=False)
#     return b, a

# def butter_lowpass_filter(data, cutoff, fs, order=5):
#     b, a = butter_lowpass(cutoff, fs, order=order)
#     y = lfilter(b, a, data)
#     return y

plt.rcParams["text.usetex"] = True

# returns true if index i is distant a check_range interval from peaks 
def before_peaks(i:int, peak, check_range:int=10):
    if i + check_range > peak and i < peak:
        return True
    else:
        return False

def search_outliers(data):
    # Calculate the quartiles (25th and 75th percentiles)
    q25, q75 = np.percentile(data, 25), np.percentile(data, 75)
    # Calculate the interquartile range (IQR)
    iqr = q75 - q25

    # Calculate the lower and upper bounds for outliers
    lower_bound = q25 - 1.5 * iqr
    upper_bound = q75 + 1.5 * iqr

    return [x for x in data if x < lower_bound or x > upper_bound]

sampling = 199

td_sideview = Data.TrackingData(data_name="Side view tracking")
td_ventralview = Data.TrackingData(data_name="Ventral view tracking")

try:
    # Load the tracking datas
    td_sideview.get_data_from_file(file_path="C:/Users/Simone/Documents/DTU/Biomechanics/MouseFeatureExtraction/Data/Sideview_mouse 35_Run_1.csv")
    td_ventralview.get_data_from_file(file_path="C:/Users/Simone/Documents/DTU/Biomechanics/MouseFeatureExtraction/Data/Ventralview_mouse 35_Run_1.csv")

    # Load the video datas
    vid_sideview = Data.VideoData(data_name="Side view video", file_path="C:/Users/Simone/Documents/DTU/Biomechanics/MouseFeatureExtraction/Videos/Sideview_mouse 35_Run_1.mp4")
    vid_ventral = Data.VideoData(data_name="Ventral view video", file_path="C:/Users/Simone/Documents/DTU/Biomechanics/MouseFeatureExtraction/Videos/Ventralview_mouse 35_Run_1.mp4")
except Data.DataFileException as e:
    print(e)
    exit()

# Finding the borders by using inverted signal.
# The built in dictionary is too unpredictable
borders_paw, b_paw = find_peaks(td_sideview.data["lHindpaw"].y, distance = 15, prominence = (0.6, None)) 
borders_fin, b_fing = find_peaks(td_sideview.data["lHindfingers"].y, distance = 15, prominence = (0.7, None))

# plt.figure(1)
# plt.plot(td_sideview.data["lHindpaw"].y, label = "L hindpaw")
# plt.plot(td_sideview.data["lHindfingers"].y, label = "L hindfingers")
# plt.plot(borders_paw, np.array(td_sideview.data["lHindpaw"].y)[borders_paw], "x")
# plt.plot(borders_fin, np.array(td_sideview.data["lHindfingers"].y)[borders_fin], "x")
# plt.title("Border detection")
# plt.xlabel("Frames")
# plt.ylabel("Height [cm]")
# plt.grid()
# plt.legend()
# plt.show(block=False)

# Finding the peaks
td_sideview.reverse_origin()
peaks_paw, p_paw = find_peaks(td_sideview.data["lHindpaw"].y, distance = 15, prominence = (0.6, None)) 
peaks_fin, p_fing = find_peaks(td_sideview.data["lHindfingers"].y, distance = 15, prominence = (0.7, None))

# plt.figure(2)
# plt.plot(td_sideview.data["lHindpaw"].y, label = "L hindpaw")
# plt.plot(td_sideview.data["lHindfingers"].y, label = "L hindfingers")
# plt.plot(peaks_paw, np.array(td_sideview.data["lHindpaw"].y)[peaks_paw], "x")
# plt.plot(peaks_fin, np.array(td_sideview.data["lHindfingers"].y)[peaks_fin], "x")
# plt.title("Peak detection")
# plt.xlabel("Frames")
# plt.ylabel("Height [cm]")
# plt.grid()
# plt.legend()
# plt.show(block=False)

# Velocity calculation
# from scipy.signal import butter, lfilter

timesteps = td_sideview.get_timesteps(sampling)
v_fing = np.diff(td_sideview.data["lHindfingers"].y) / np.diff(timesteps)
# v_fing_filtered = butter_lowpass_filter(v_fing, 25 ,sampling)
v_paw = np.diff(td_sideview.data["lHindpaw"].y) / np.diff(timesteps)

plt.figure(3)
plt.plot(v_paw, label = r'$v_{paw}^L$')
plt.plot(v_fing, label = r"$v_{fin}^L$")
#plt.plot(v_fing_filtered, label = r"$v_{filt}^L$")

# Touchdown detection
touchdowns = []

for i in range(len(borders_fin)):
    if borders_fin[i] < borders_paw[i]:
        touchdowns.append(borders_fin[i])
    else:
        touchdowns.append(borders_paw[i])

# Swing detection

swings = []
steps = np.diff(touchdowns)

for i,td in enumerate(touchdowns[:-1]):
    outliers = search_outliers(v_fing)
    step_mean = np.mean(np.abs(v_fing[td:td+steps[i]]))
    for j in range(steps[i]):
        # if v_fing[td+j] > step_mean and around_peaks(td+j, peaks_paw[i]):
        #     swings.append(td+j)
        #     break
        if v_fing[td+j] in outliers and before_peaks(td+j, peaks_paw[i]):
            swings.append(td+j)
            #break
    if i == 0:
        plt.plot(np.arange(td,td+steps[i]), np.ones(len(v_fing[td:td+steps[i]]))*step_mean,'r', label = r"$avg_{Step}$")
    else:
        plt.plot(np.arange(td,td+steps[i]), np.ones(len(v_fing[td:td+steps[i]]))*step_mean,'r')
plt.title("Velocity and acceleration analysis")
plt.xlabel("Frames")
plt.ylabel("Height [cm]")
plt.grid()
plt.legend()
plt.show(block=False)

plt.figure(4)
plt.plot(td_sideview.data["lHindpaw"].y, label = "L hindpaw")
plt.plot(td_sideview.data["lHindfingers"].y, label = "L hindfingers")
plt.plot(swings, np.array(td_sideview.data["lHindpaw"].y)[swings], "r^")
plt.plot(swings, np.array(td_sideview.data["lHindfingers"].y)[swings], "r^", label = "swings")
plt.plot(touchdowns, np.array(td_sideview.data["lHindfingers"].y)[touchdowns], "gv")
plt.plot(touchdowns, np.array(td_sideview.data["lHindpaw"].y)[touchdowns], "gv", label = "touchdowns")
plt.plot(peaks_paw, np.array(td_sideview.data["lHindpaw"].y)[peaks_paw], "b*")
plt.plot(peaks_fin, np.array(td_sideview.data["lHindfingers"].y)[peaks_fin], "b*", label = "peaks")
plt.title("Swings and Touchdown detection")
plt.xlabel("Frames")
plt.ylabel("Height [cm]")
plt.grid()
plt.legend()
plt.show()

# Cut halfsteps by looking at first and last touchdown
lower_t = min([min(borders_fin), min(borders_paw)])
upper_t = max([max(borders_fin), max(borders_paw)])

td_sideview.data.cut_step(lower_t, upper_t)
td_sideview.data.cut_time(lower_t, upper_t, sampling)
