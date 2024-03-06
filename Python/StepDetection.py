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


# Finding the peaks
td_sideview.reverse_origin()
peaks_paw, _paw = find_peaks(td_sideview.data["lHindpaw"].y, distance = 10, prominence = (0.5, None)) 
peaks_fin, _fing = find_peaks(td_sideview.data["lHindfingers"].y, distance = 10, prominence = (0.5, None))

plt.figure()
plt.plot(td_sideview.data["lHindpaw"].y, label = "L hindpaw")
plt.plot(td_sideview.data["lHindfingers"].y, label = "L hindfingers")
plt.plot(peaks_paw, np.array(td_sideview.data["lHindpaw"].y)[peaks_paw], "x")
plt.plot(peaks_fin, np.array(td_sideview.data["lHindfingers"].y)[peaks_fin], "x")
plt.xlabel("Frames")
plt.ylabel("Height [cm]")
plt.grid()
plt.legend()
plt.show()

# Velocity calculation
timesteps = td_sideview.get_timesteps(sampling)
v_fing = np.diff(td_sideview.data["lHindfingers"].y) / np.diff(timesteps)
v_paw = np.diff(td_sideview.data["lHindpaw"].y) / np.diff(timesteps)

plt.figure()
plt.plot(v_paw, label = r'$v_{paw}^L$')
plt.plot(v_fing, label = r"$v_{fin}^L$")
plt.xlabel("Frames")
plt.ylabel("Height [cm]")
plt.grid()
plt.legend()
plt.show()

# Border detection
