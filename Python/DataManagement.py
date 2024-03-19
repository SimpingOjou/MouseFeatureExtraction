# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 17:03:31 2024

@author: walid
"""

from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np

from GUI import GUI
import os
import csv
import cv2
import numpy as np

from math import dist
from WorldFrame import WorldFrame


class GetDataException(Exception):
    """Raise for errors when attempting to read a data file"""


# Check that all the elements in a list are equal
def all_same(items):
    return len(set(items)) < 2


# Base class for opening data files
class OpenableDataFile:
    def __init__(self, data_name:str, file_path:str, initial_dir:str, file_types, data_ext):
        # Ask to pick a path if none is given
        if file_path is None:
            ui = GUI()
            file_path = ui.ask_data_file(data_name, initial_dir=initial_dir, filetypes=file_types)
        
        # Check that the file exists
        if file_path == "" or not os.path.exists(file_path):
            raise GetDataException("Error : '" + file_path + "' is not a valid file path")
        
        # Save the file parameters in the object
        self.file_path = file_path
        self.name = data_name

        # Extract the directory, name and extension of the file
        basename = os.path.basename(file_path)
        self.file_name, self.file_ext = os.path.splitext(basename)
        self.file_dir = os.path.dirname(file_path)

        # Check that the file extension is valid
        if self.file_ext not in data_ext:
            raise GetDataException("Error : '" + self.file_ext + "' is not a valid data extension")



# Class containing the data of a body part for a single frame
class BodyPart:
    def __init__(self, x_data, y_data, bodypart_name, likelihood_data=[], z_data=[]):
        self.name = bodypart_name
        self.x = np.array(x_data)
        self.y = np.array(y_data)
        self.z = np.array(z_data)

        self.likelihood = np.array(likelihood_data)

    # Returns the coordinates (x,y) of the tracked body part at frame frame_num
    def get_2D_coord_at_frame(self, frame_num:int):
        return (self.x[frame_num], self.y[frame_num])
    
    # Returns the coordinates (x,y,z) of the tracked body part at frame frame_num
    def get_3D_coord_at_frame(self, frame_num:int):
        return (self.x[frame_num], self.y[frame_num], self.z[frame_num])
    
    # Returns true if the parameters have the same number of frames
    def check_frame_equality(self):
        return self.x.size == self.y.size and (self.likelihood.size==0 or self.likelihood.size == self.x.size) and (self.z.size==0 or self.z.size == self.x.size)
    
    # Returns the total number of frames
    def get_total_frames(self):
        if not self.check_frame_equality():
            raise GetDataException("The data for the BodyPart '" + self.name + "' don't have the same number of frames")

        return len(self.x)
    
    # Adds the given coordinates to the BodyPart (2D or 3D)
    def add_frame_from_coord(self, coord):
        self.x.append(coord[0])
        self.y.append(coord[1])
        
        if len(coord) > 2:
            self.z.append(coord[2])

    # Print on the command line the data contained in the limb at frame frame_num
    def print_data_at_frame(self, frame_num:int):
        str_to_print = "("

        if len(self.x) > frame_num:
            str_to_print += f"{self.x[frame_num]}"
        
        if len(self.y) > frame_num:
            str_to_print += f", {self.y[frame_num]}"

        if len(self.z) > frame_num:
            str_to_print += f", {self.z[frame_num]}"
        
        str_to_print += ")"

        if len(self.likelihood) > frame_num:
            str_to_print += f" - {self.likelihood[frame_num]}"

        print(str_to_print)



# Class managing the tracking data
class TrackingData(OpenableDataFile):
    # File types allowed when asking the user to pick the data file
    filetypes = (('CSV', '*.csv'),('All files', '*.*'))
    # Initial directory when asking the user to pick the data file
    initial_dir = '.'
    # Extensions allowed for a data file
    data_ext = [".csv",".txt"]

    # Name of the corresponding columns on the traking file
    x_col_name = "x"
    y_col_name = "y"
    likelihood_col_name = "likelihood"

    def __init__(self, data_name:str):
        self.name = data_name

        # Create the tracking data dictionnary
        self.data : dict[str, BodyPart] = dict()

        self.total_frames = 0


    # Converts the data from the 2 camera views to the world frame, using world_frame
    def get_3D_data(self, world_frame:WorldFrame, side_tracking_data:dict[str, BodyPart], ventral_tracking_data:dict[str, BodyPart]):
        side_frames = [bp.get_total_frames() for bp in side_tracking_data.values()]
        ventral_frames = [bp.get_total_frames() for bp in ventral_tracking_data.values()]
        
        # If the side and ventral data don't have the same number of frames
        if not all_same(side_frames + ventral_frames):
            raise GetDataException("The dictionnaries for side and ventral tracking data don't have the same number of frames")

        self.total_frames = side_frames[0]

        common_keys = side_tracking_data.keys() & ventral_tracking_data.keys()

        # If there is no common feature tracked
        if len(common_keys) == 0:
            raise GetDataException("Side and ventral tracking data have no common features")
        
        for body_part_name in common_keys:
            side_bp = side_tracking_data[body_part_name]
            ventral_bp = ventral_tracking_data[body_part_name]

            x_coord = []
            y_coord = []
            z_coord = []
            
            for frame in range(self.total_frames):
                side_screen_coord = side_bp.get_2D_coord_at_frame(frame)
                ventral_screen_coord = ventral_bp.get_2D_coord_at_frame(frame)

                world_coord = world_frame.to_3D(side_screen_coord, ventral_screen_coord)

                #self.data[body_part_name].add_frame_from_coord(world_coord)
                x_coord.append(world_coord[0])
                y_coord.append(world_coord[1])
                z_coord.append(world_coord[2])

            self.data[body_part_name] = BodyPart(x_data=x_coord, y_data=y_coord, z_data=z_coord, bodypart_name=body_part_name)
        
    
    # Load the data from a CSV file (ask the user for the file if no file_path is provided)
    def get_data_from_file(self, file_path:str=None, data_delimiter:str=',', bodypart_row_name:str="bodyparts", coord_row_name:str="coords"):
        # Get the data from the file
        super().__init__(self.name, file_path, initial_dir=self.initial_dir, file_types=self.filetypes, data_ext=self.data_ext)

        # Open the data file and extract the data
        with open(self.file_path, mode="r") as data_file:
            csv_reader = csv.reader(data_file, delimiter=data_delimiter)

            # Temporary values
            all_bodyparts = [""]
            x_col = []
            y_col = []
            likelihood_col = []

            x_data : dict[str, list] = dict()
            y_data : dict[str, list] = dict()
            likelihood_data : dict[str, list] = dict()

            # Read each row of the data file
            for row in csv_reader:
                # If it's the bodyparts row, create the bodyparts in the data dictionnary
                if row[0] == bodypart_row_name:
                    for bodypart in row[1:]:
                        #self.data[bodypart] = BodyPart(bodypart)
                        all_bodyparts.append(bodypart)

                # If it's the coordinate (x,y,likelihood) column, save the indices
                elif row[0] == coord_row_name:
                    for i in range(1,len(row)):
                        if row[i] == self.x_col_name:
                            x_col.append(i)
                        elif row[i] == self.y_col_name:
                            y_col.append(i)
                        elif row[i] == self.likelihood_col_name:
                            likelihood_col.append(i)
                        else:
                            raise Exception("Error in row '" + coord_row_name + "' : '" + row[i] + "' at column " + i + " is not a valid column name")
                
                # If the value is an integer (ie is a frame number),
                # add the tracking values of that frame to the data of the corresponding bodypart
                elif row[0].isdigit():
                    for i in x_col:
                        bodypart = all_bodyparts[i]
                        #self.data[bodypart].x.append(float(row[i]))
                        if not bodypart in x_data.keys():
                            x_data[bodypart] = [float(row[i])]
                        else:
                            x_data[bodypart].append(float(row[i]))

                    for i in y_col:
                        bodypart = all_bodyparts[i]
                        #self.data[bodypart].y.append(float(row[i]))
                        if not bodypart in y_data.keys():
                            y_data[bodypart] = [float(row[i])]
                        else:
                            y_data[bodypart].append(float(row[i]))
                    
                    for i in likelihood_col:
                        bodypart = all_bodyparts[i]
                        #self.data[bodypart].likelihood.append(float(row[i]))
                        if not bodypart in likelihood_data.keys():
                            likelihood_data[bodypart] = [float(row[i])]
                        else:
                            likelihood_data[bodypart].append(float(row[i]))

            for bodypart in all_bodyparts[1:]:
                # self.data[bodypart].x = np.array(self.data[bodypart].x)
                # self.data[bodypart].y = np.array(self.data[bodypart].y)
                # self.data[bodypart].likelihood = np.array(self.data[bodypart].likelihood)
                self.data[bodypart] = BodyPart(x_data=x_data[bodypart], y_data=y_data[bodypart], likelihood_data=likelihood_data[bodypart], bodypart_name=bodypart)

        # Check that all the BodyParts have the same number of frames
        all_frames = [bp.get_total_frames() for bp in self.data.values()]
        if not all_same(all_frames):
            raise GetDataException("All the BodyParts from " + self.name + " don't have the same number of frames")
        
        self.total_frames = all_frames[0]

    def compensate_cropping(self, cropping_coord:tuple[int, int]):
        for bp in self.data.values():
            bp.x += cropping_coord[0]
            bp.y += cropping_coord[1]

    # Returns the total frame number of the tracking data
    def get_total_frames(self):
        key = next(iter(self.data))
        return self.data[key].get_total_frames()

    # Returns the total time of the tracking data
    def get_total_time(self, sampling:float):
        return self.get_total_frames() / sampling
    
    # Returns the time divided in timesteps as an array
    def get_timesteps(self, sampling):
        return np.linspace(0, self.get_total_time(sampling), num = self.get_total_frames()) 

    # Converting the data to the opposite origin 
    # (upper-left to bottom-right, upper-right to bottom-left, ...)
    def reverse_origin(self):
        x_max = max([max(bp.x) for bp in self.data.values()])
        y_max = max([max(bp.y) for bp in self.data.values()])

        for part in self.data:
            self.data[part].x = x_max - self.data[part].x
            self.data[part].y = y_max - self.data[part].y

    # Cuts out the first and last steps
    def cut_step(self, lower_t, upper_t):
        for bodypart in self.data:
            self.data[bodypart].x = self.data[bodypart].x[lower_t:upper_t + 1]
            self.data[bodypart].y = self.data[bodypart].y[lower_t:upper_t + 1]
            self.data[bodypart].likelihood = self.data[bodypart].likelihood[lower_t:upper_t + 1]
            
    # Cut time 
    def cut_time(self, lower_t, upper_t, sampling):
        return self.get_timesteps(sampling)[lower_t:upper_t + 1]

    
    def vizualize_frames_3D(self, xlim=[], ylim=[], zlim=[], scatter_point_marker='o'):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        title = ax.set_title('3D projection')

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_zlim(zlim)

        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')

        data_x = []
        data_y = []
        data_z = []

        for bp in self.data.values():
            x,y,z = bp.get_3D_coord_at_frame(0)
            data_x.append(x)
            data_y.append(y)
            data_z.append(z)
            
        graph, = ax.plot(data_x, data_y, data_z, marker=scatter_point_marker, linestyle='None')
        
        def update(frame):
            data_x = []
            data_y = []
            data_z = []

            for bp in self.data.values():
                x,y,z = bp.get_3D_coord_at_frame(frame)
                data_x.append(x)
                data_y.append(y)
                data_z.append(z)
            
            ax.set_title('3D projection frame ' + str(frame))
            
            graph.set_data(data_x, data_y)
            graph.set_3d_properties(data_z)

            return title, graph,

        ani = animation.FuncAnimation(fig=fig, func=update, frames=self.total_frames, interval=1/30, blit=False)
        plt.show()



from Camera import CameraData

# Class managing video data
class VideoData(OpenableDataFile):
    # File types allowed when asking the user to pick the data file
    filetypes = (('mp4', '*.mp4'), ('avi', '*.avi'),('All files', '*.*'))
    # Initial directory when asking the user to pick the data file
    initial_dir = '.'
    # Extensions allowed for a data file
    data_ext = [".mp4",".avi"]

    def __init__(self, camera:CameraData, data_name:str, file_path:str=None):
        # Get the data from the file
        super().__init__(data_name, file_path, initial_dir=self.initial_dir, file_types=self.filetypes, data_ext=self.data_ext)

        # Get the video at the given filepath
        self.vidcap = cv2.VideoCapture(self.file_path)
        
        # Get the frames per second
        self.fps = self.vidcap.get(cv2.CAP_PROP_FPS) 

        # Get the total numer of frames in the video.
        self.frame_count = self.vidcap.get(cv2.CAP_PROP_FRAME_COUNT)

        # Calculate the duration of the video in seconds
        self.duration = self.frame_count / self.fps

        # Variable containing the coordinates pointed on an image
        self.pointed_coord = None

        # Default calibration value
        self.origin_screen_x = 0
        self.origin_screen_y = 0

        # Default focal length of the camera
        self.camera = camera

    
    # Estimates the focal length by pointing at two marks at distance_camera_marks from the camera
    # and separated by a distance of distance_btw_marks,
    def estimate_focal_length(self, frame_num:int, distance_camera_marks:float, world_distance_btw_marks:float):
        # Get the 2 marks' position
        pointed_coord_1 = self.point_at(frame_num, window_name="Point at the first mark")
        pointed_coord_2 = self.point_at(frame_num, window_name="Point at the second mark")

        screen_dist_btw_marks = dist(pointed_coord_1, pointed_coord_2)

        focal_length_px = distance_camera_marks * screen_dist_btw_marks / world_distance_btw_marks

        return focal_length_px * self.camera.pixel_size


    # Setup the calibration paremeters to adjust for variations between the video and the tracked points
    def calibrate(self, frame_num:int, pos_to_point_at_name:str, expected_coord:tuple[int, int]):
        # Reset the calibration parameters
        self.origin_screen_x = 0
        self.origin_screen_y = 0

        # Ask the user to point at the required tracking data
        pointed_x, pointed_y = self.point_at(frame_num, window_name="Point at " + pos_to_point_at_name)

        # Calculate the transformation from tracking data screen coordinates to current video screen coordinates
        expected_x, expected_y = expected_coord

        # Determine the origin point of the tracking data
        self.origin_screen_x = pointed_x - expected_x
        self.origin_screen_y = pointed_y - expected_y


    # Converts the coordinates from screen space to tracking data space (ie with the same origin,... as the tracking data)
    def to_tracking_space(self, coord:tuple[int, int]):
        tracked_space_pointed_x = abs(coord[0] - self.origin_screen_x)
        tracked_space_pointed_y = abs(coord[1] - self.origin_screen_y)

        return tracked_space_pointed_x, tracked_space_pointed_y


    # Shows the frame frame_num of the video, in a window named window_name (if provided, otherwise auto generated)
    # And allow the user to click on a point, before returning the coordinates of the click in the screen space
    # The coordinates are returned in tracking data frame
    def point_at(self, frame_num:int, window_name:str=None):
        # Reset the pointed coordinates value and last key pressed
        self.pointed_coord = None
        key_pressed = None

        # While there is no pointed coordinates AND the user didn't close the window
        while self.pointed_coord is None and key_pressed != -1:
            key_pressed = self.show_frame(frame_num, img_name=window_name, mouse_callback_func=self.__get_point_click_event)

        # If the user closed the window without pointing, exit the program
        if self.pointed_coord is None or key_pressed == -1:
            exit()

        return self.to_tracking_space(self.pointed_coord)
    

    # Shows the frame frame_num of the video, in a window named img_name (if provided, otherwise auto generated name)
    # And add the callback function mouse_callback_func on mouse events (if provided)
    def show_frame(self, frame_num:int, img_name:str=None, mouse_callback_func=None):
        # Set the video to the required frame
        self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

        # Try to read the frame
        success, image = self.vidcap.read()

        # If the frame couldn't be read
        if not success:
            print("Failed to read the frame " + str(frame_num) + " from the video file at " + self.file_path)
            return None

        # Auto generate the image name if not given
        if img_name is None:
            img_name = self.file_name+' frame '+ str(frame_num)

        #Display the resulting frame
        cv2.imshow(img_name, image)

        # Set the mouse handler for the image if needed
        if mouse_callback_func is not None:
            cv2.setMouseCallback(img_name, 
                                    lambda *args, **kwargs: mouse_callback_func(image, img_name, *args, **kwargs))

        # Wait for a key press and return it after closing the window
        key_pressed = cv2.waitKey(0)
        cv2.destroyAllWindows()

        return key_pressed
            


    # Callback function allowing the user to point and click on the displayed image
    # The coordinates of the clicked point are stored in self.pointed_coord, and a dot appears on screen at that position
    def __get_point_click_event(self, 
                                  image, img_name, 
                                  event, x, y, flags, params):
        # checking for left mouse clicks 
        if event == cv2.EVENT_LBUTTONDOWN: 
            img = image.copy()

            print("Pointed position :", x, ' ', y)
            print("In tracking space :", self.to_tracking_space((x,y))) 

            # Set the pointed coordinates
            self.pointed_coord = (x,y)

            img = cv2.circle(img, (x,y), radius=0, color=(255, 0, 0), thickness=-1)

            cv2.imshow(img_name, img)


    # Releases the video when the instance is destroyed
    def __del__(self):
        # Release the video when deleting the instance
        if hasattr(self, 'vidcap'):
            self.vidcap.release()
    
