import DataManagement as Data
import WorldFrame as WF
import GUI as UI

from time import sleep

# Parameters
camera_pixel_size = 4.8e-6

side_ventral_cam_dist_vertical = 0.93

distance_side_cam_marks = 0.53
distance_ventral_cam_marks = 0.54

# Cropping coordinates (x1, y1, x2, y2) (upper-left and lower-right)
deeplabcut_cropping_side = (20, 300, 690, 610)
deeplabcut_cropping_ventral = (20, 48, 690, 266)

# Coordinates of upper-left and lower right of the windows in the video
ventral_window_coord = (30, 50, 687, 253)
side_window_coord = (30, 304, 687, 507)



side_window_video_dimensions = (side_window_coord[2] - side_window_coord[0], side_window_coord[3] - side_window_coord[1])
ventral_window_video_dimensions = (ventral_window_coord[2] - ventral_window_coord[0], ventral_window_coord[3] - ventral_window_coord[1])


# Initialize the tracking data (no data loaded yet)
td_sideview = Data.TrackingData(data_name="Side view tracking")
td_ventralview = Data.TrackingData(data_name="Ventral view tracking")

# Initializa the cameras
camera_side = Data.CameraData(focal_length=None, pixel_size=camera_pixel_size, resolution=side_window_video_dimensions)
camera_ventral = Data.CameraData(focal_length=None, pixel_size=camera_pixel_size, resolution=ventral_window_video_dimensions)

try:
    # Load the tracking datas
    td_sideview.get_data_from_file(file_path="./Data/Sideview_mouse 35_Run_1.csv")
    td_ventralview.get_data_from_file(file_path="./Data/Ventralview_mouse 35_Run_1.csv")

    # Load the video datas
    vid_sideview = Data.VideoData(camera=camera_side, data_name="Side view video", file_path="./Videos/Sideview_mouse 35_Run_1.mp4")
    vid_ventral = Data.VideoData(camera=camera_ventral, data_name="Ventral view video", file_path="./Videos/Ventralview_mouse 35_Run_1.mp4")
except Data.GetDataException as e:
    print(e)
    exit()


td_sideview.compensate_cropping(deeplabcut_cropping_side)
td_ventralview.compensate_cropping(deeplabcut_cropping_ventral)

# td_sideview.data["head"].print_data_at_frame(0)
# td_ventralview.data["head"].print_data_at_frame(0)


# Calibrate the video datas to compensate for margins,... between the tracked data and the videos
frame_num = 0
# vid_sideview.calibrate(frame_num, "head on side view", td_sideview.data["head"].get_coord_at_frame(frame_num))
# vid_ventral.calibrate(frame_num, "head on ventral view", td_ventralview.data["head"].get_coord_at_frame(frame_num))


# Estimate the focal length of the cameras

# distance_btw_marks = 0.5
# camera_side.focal_length = vid_sideview.estimate_focal_length(frame_num, distance_side_cam_marks, distance_btw_marks)
# camera_ventral.focal_length = vid_ventral.estimate_focal_length(frame_num, distance_ventral_cam_marks, distance_btw_marks)

# print("Side focal lenght :", vid_sideview.camera.focal_length)
# print("Ventral focal length :", vid_ventral.camera.focal_length)

# Or set it up (faster for debug BUT should be estimated for each data since the parameters of the camera may change)
camera_side.focal_length = 0.0027578133406769936
camera_ventral.focal_length = 0.00270609268928616


#print(td_sideview.data["head"].get_2D_coord_at_frame(frame_num))
print(td_ventralview.data["head"].get_2D_coord_at_frame(frame_num))

# Get the mark's coordinate in the same frame as the tracking data
mark_screen_coord_side = vid_sideview.point_at(frame_num, "Point at the mark on the side view camera")
mark_screen_coord_ventral = vid_ventral.point_at(frame_num, "Point at the mark on the ventral view camera")

# Convert from 2D to 3D
wf = WF.WorldFrame(distance_side_cam_marks, distance_ventral_cam_marks, side_ventral_cam_dist_vertical, 
                   mark_screen_coord_side, mark_screen_coord_ventral, 
                   vid_sideview.camera, vid_ventral.camera)

tracking_data_3D = Data.TrackingData("3D tracking data")
tracking_data_3D.get_3D_data(wf, td_sideview.data, td_ventralview.data)

tracking_data_3D.vizualize_frames_3D(xlim=[-0.4, 0.4], ylim=[-0.2, 0.2], zlim=[0, 0.1])



# Print the x coordinate of the head at frame 200 
print(td_sideview.data["head"].x[200])

# Print the y coordinate of the anckle at frame 143 
print(td_sideview.data["anckle"].x[143])

# Print the likelihood for the left hindfinger tracking at the last frame 
print(td_sideview.data["lHindfingers"].x[-1])

