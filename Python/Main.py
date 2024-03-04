import DataManagement as Data
import WorldFrame as WF
import GUI as UI

# Load the tracking datas
try:
    td_sideview = Data.TrackingData(data_name="Side view", file_path="./Data/Sideview_mouse 35_Run_1.csv")
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

try:
    experiment_vid = Data.VideoData(data_name="Experiment video", file_path="./Videos/Dual_side_and_ventral_Mouse22_CnF_1wPostSCI_Test_Corridor_Left_Run1DLC_resnet50_Corridor_sideviewJul22shuffle1_1030000_labeled.mp4")
except Data.DataFileException as e:
    print(e)
    exit()

experiment_vid.show_frame(0)

#world_frame = WF.WorldFrame()