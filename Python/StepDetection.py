# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 23:19:00 2024

@author: simone
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import DataManagement as Data

plt.rcParams["text.usetex"] = True

try:
    td_sideview = Data.TrackingData(data_name="Side view", file_path="./Data/Sideview_mouse 35_Run_1.csv")
except Data.DataFileException as e:
    print(e)
    exit()

try:
    td_ventralview = Data.TrackingData(data_name="Ventral view", file_path="./Data/Ventralview_mouse 35_Run_1.csv")
except Data.DataFileException as e:
    print(e)
    exit()

sampling = 199
cf = 18.8

print(td_sideview.data["head"].x[200])
print(td_sideview.get_time(sampling))

td_sideview.convert_origin(cf)
print(td_sideview.data["head"].x[200])