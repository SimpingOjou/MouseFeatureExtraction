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

plt.rcParams["text.usetex"] = True

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

plt.figure(1)
plt.plot(td_sideview.data["lHindpaw"].y, label = "L hindpaw")
plt.plot(td_sideview.data["lHindfingers"].y, label = "L hindfingers")
plt.plot(borders_paw, np.array(td_sideview.data["lHindpaw"].y)[borders_paw], "x")
plt.plot(borders_fin, np.array(td_sideview.data["lHindfingers"].y)[borders_fin], "x")
plt.title("Border detection")
plt.xlabel("Frames")
plt.ylabel("Height [cm]")
plt.grid()
plt.legend()
plt.show(block=False)

# Finding the peaks
td_sideview.reverse_origin()
peaks_paw, p_paw = find_peaks(td_sideview.data["lHindpaw"].y, distance = 15, prominence = (0.6, None)) 
peaks_fin, p_fing = find_peaks(td_sideview.data["lHindfingers"].y, distance = 15, prominence = (0.7, None))

plt.figure(2)
plt.plot(td_sideview.data["lHindpaw"].y, label = "L hindpaw")
plt.plot(td_sideview.data["lHindfingers"].y, label = "L hindfingers")
plt.plot(peaks_paw, np.array(td_sideview.data["lHindpaw"].y)[peaks_paw], "x")
plt.plot(peaks_fin, np.array(td_sideview.data["lHindfingers"].y)[peaks_fin], "x")
plt.title("Peak detection")
plt.xlabel("Frames")
plt.ylabel("Height [cm]")
plt.grid()
plt.legend()
plt.show(block=False)

# Velocity calculation
timesteps = td_sideview.get_timesteps(sampling)
v_fing = np.diff(td_sideview.data["lHindfingers"].y) / np.diff(timesteps)
v_paw = np.diff(td_sideview.data["lHindpaw"].y) / np.diff(timesteps)

plt.figure(3)
plt.plot(v_paw, label = r'$v_{paw}^L$')
plt.plot(v_fing, label = r"$v_{fin}^L$")
plt.title("Velocity analysis")
plt.xlabel("Frames")
plt.ylabel("Height [cm]")
plt.grid()
plt.legend()
plt.show()

# Touchdown detection
touchdowns = []

for i in range(len(borders_fin)):
    if borders_fin[i] < borders_paw:
        touchdowns.append(borders_fin[i])
    else:
        touchdowns.append(borders_paw[i])

# Swing detection



# Cut halfsteps by looking at first and last touchdown
lower_t = min([min(borders_fin), min(borders_paw)])
upper_t = max([max(borders_fin), max(borders_paw)])

td_sideview.data.cut_step(lower_t, upper_t)
td_sideview.data.cut_time(lower_t, upper_t, sampling)
