import DataManagement as Data
import WorldFrame as WF
import GUI as UI

td_sideview = Data.TrackingData(data_name="Side view tracking")
td_ventralview = Data.TrackingData(data_name="Ventral view tracking")

try:
    # Load the tracking datas
    td_sideview.get_data_from_file(file_path="./Data/Sideview_mouse 35_Run_1.csv")
    td_ventralview.get_data_from_file(file_path="./Data/Ventralview_mouse 35_Run_1.csv")

    # Load the video datas
    vid_sideview = Data.VideoData(data_name="Side view video", file_path="./Videos/Sideview_mouse 35_Run_1.mp4")
    vid_ventral = Data.VideoData(data_name="Ventral view video", file_path="./Videos/Ventralview_mouse 35_Run_1.mp4")
except Data.DataFileException as e:
    print(e)
    exit()

# td_sideview.data["head"].print_data_at_frame(0)
# td_ventralview.data["head"].print_data_at_frame(0)

# Calibrate the video datas to compensate for margins,... between the tracked data and the videos
frame_num = 0
vid_sideview.calibrate(frame_num, "head on side view", td_sideview.data["head"].get_coord_at_frame(frame_num))
vid_ventral.calibrate(frame_num, "head on ventral view", td_ventralview.data["head"].get_coord_at_frame(frame_num))


# Estimate the focal length of the cameras
distance_side_cam_marks = 1
distance_ventral_cam_marks = 1
distance_btw_marks = 0.5
vid_sideview.estimate_focal_length(frame_num, distance_side_cam_marks, distance_btw_marks)
vid_ventral.estimate_focal_length(frame_num, distance_ventral_cam_marks, distance_btw_marks)


# Get the mark's coordinate in the same frame as the tracking data
mark_screen_coord_side = vid_sideview.point_at(frame_num, "Point at the mark on the side view camera")
mark_screen_coord_ventral = vid_ventral.point_at(frame_num, "Point at the mark on the ventral view camera")


# Convert from 2D to 3D
side_ventral_cam_dist_vertical = 2
side_cam_screen_resolution = (640, 180)
ventral_cam_screen_resolution = (640, 180)
wf = WF.WorldFrame(distance_side_cam_marks, distance_ventral_cam_marks, side_ventral_cam_dist_vertical, 
                   mark_screen_coord_side, mark_screen_coord_ventral, 
                   vid_sideview.focal_length, vid_ventral.focal_length, 
                   side_cam_screen_resolution, ventral_cam_screen_resolution)


# Print the x coordinate of the head at frame 200 
print(td_sideview.data["head"].x[200])

# Print the y coordinate of the anckle at frame 143 
print(td_sideview.data["anckle"].x[143])

# Print the likelihood for the left hindfinger tracking at the last frame 
print(td_sideview.data["lHindfingers"].x[-1])

