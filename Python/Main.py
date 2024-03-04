import DataManagement as Data

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


# Print the x coordinate of the head at frame 200 
print(td_sideview.data["head"].x[200])

# Print the y coordinate of the anckle at frame 143 
print(td_sideview.data["anckle"].x[143])

# Print the likelihood for the left hindfinger tracking at the last frame 
print(td_sideview.data["lHindfingers"].x[-1])
