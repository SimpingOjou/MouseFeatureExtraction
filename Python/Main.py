import DataManagement as Data
import WorldFrame as WF
import GUI as UI

# Load the tracking datas
try:
    td_sideview = Data.TrackingData(data_name="Side view tracking", file_path="./Data/Sideview_mouse 35_Run_1.csv")
    td_ventralview = Data.TrackingData(data_name="Ventral view tracking", file_path="./Data/Ventralview_mouse 35_Run_1.csv")
except Data.DataFileException as e:
    print(e)
    exit()


# Print the x coordinate of the head at frame 200 
print(td_sideview.data["head"].x[200])

# Print the y coordinate of the anckle at frame 143 
print(td_sideview.data["anckle"].x[143])

# Print the likelihood for the left hindfinger tracking at the last frame 
print(td_sideview.data["lHindfingers"].x[-1])

try:
    vid_sideview = Data.VideoData(data_name="Side view video", file_path="./Videos/Sideview_mouse 35_Run_1.mp4")
    vid_ventral = Data.VideoData(data_name="Ventral view video", file_path="./Videos/Ventralview_mouse 35_Run_1.mp4")
except Data.DataFileException as e:
    print(e)
    exit()

td_sideview.data["head"].show_frame(0)
vid_sideview.calibrate(0, "head", td_sideview.data["head"].x, td_sideview.data["head"].y)
vid_sideview.show_frame(0)

#world_frame = WF.WorldFrame()