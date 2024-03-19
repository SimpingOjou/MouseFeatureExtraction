# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 17:03:31 2024

@author: walid
"""

from GUI import GUI
import os
import csv
import cv2
import numpy as np

from math import dist


class DataFileException(Exception):
    """Raise for errors when attempting to read a data file"""



# Base class for opening data files
class OpenableDataFile:
    def __init__(self, data_name, file_path, initial_dir, file_types, data_ext):
        # Ask to pick a path if none is given
        if file_path is None:
            ui = GUI()
            file_path = ui.ask_data_file(data_name, initial_dir=initial_dir, filetypes=file_types)
        
        # Check that the file exists
        if file_path == "" or not os.path.exists(file_path):
            raise DataFileException("Error : '" + file_path + "' is not a valid file path")
        
        # Save the file parameters in the object
        self.file_path = file_path
        self.name = data_name

        # Extract the directory, name and extension of the file
        basename = os.path.basename(file_path)
        self.file_name, self.file_ext = os.path.splitext(basename)
        self.file_dir = os.path.dirname(file_path)

        # Check that the file extension is valid
        if self.file_ext not in data_ext:
            raise DataFileException("Error : '" + self.file_ext + "' is not a valid data extension")



# Class containing the data of a body part for a single frame
class BodyPart:
    def __init__(self, x_data, y_data, likelihood_data, bodypart_name):
        self.name = bodypart_name
        self.x = np.array(x_data)
        self.y = np.array(y_data)
        self.z = np.array([])
        self.likelihood = np.array(likelihood_data)

    # Returns the coordinates (x,y) of the tracked body part at frame frame_num
    def get_coord_at_frame(self, frame_num):
        return (self.x[frame_num], self.y[frame_num])

    # Print on the command line the data contained in the limb at frame frame_num
    def print_data_at_frame(self, frame_num):
        if len(self.z) > 0:
            print(f"({self.x[frame_num]}, {self.y[frame_num]}, {self.z[frame_num]}) - {self.likelihood[frame_num]}")
        else:
            print(f"({self.x[frame_num]}, {self.y[frame_num]}) - {self.likelihood[frame_num]}")



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

    def __init__(self, data_name):
        self.name = data_name

        # Create the tracking data dictionnary
        self.data = dict()


    # Converts the data from the 2 camera views to the world frame, using world_frame
    def get_3D_data(self, world_frame, side_tracking_data, ventral_tracking_data):
        pass

    
    # Load the data from a CSV file (ask the user for the file if no file_path is provided)
    def get_data_from_file(self, file_path=None, data_delimiter=',', bodypart_row_name="bodyparts", coord_row_name="coords"):
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
                self.data[bodypart] = BodyPart(x_data[bodypart], y_data[bodypart], likelihood_data[bodypart], bodypart)

    # Returns the total frame number of the tracking data
    def get_total_frames(self):
        key = next(iter(self.data))
        return len(self.data[key].x)

    # Returns the total time of the tracking data
    def get_total_time(self, sampling):
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



# Class managing video data
class VideoData(OpenableDataFile):
    # File types allowed when asking the user to pick the data file
    filetypes = (('mp4', '*.mp4'), ('avi', '*.avi'),('All files', '*.*'))
    # Initial directory when asking the user to pick the data file
    initial_dir = '.'
    # Extensions allowed for a data file
    data_ext = [".mp4",".avi"]

    def __init__(self, data_name, file_path=None):
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

        # Coordinate pointed on an image
        self.pointed_coord = None

        # Default calibration value
        self.origin_screen_x = 0
        self.origin_screen_y = 0

        # Default focal length of the camera
        self.focal_length = None

    
    # Estimates the focal length by pointing at two marks at distance_camera_marks from the camera
    # and separated by a distance of distance_btw_marks,
    def estimate_focal_length(self, frame_num, distance_camera_marks, world_distance_btw_marks):
        # Get the 2 marks' position
        pointed_coord_1 = self.point_at(frame_num, window_name="Point at the first mark")
        pointed_coord_2 = self.point_at(frame_num, window_name="Point at the second mark")

        screen_dist_btw_marks = dist(pointed_coord_1, pointed_coord_2)

        self.focal_length = distance_camera_marks * screen_dist_btw_marks / world_distance_btw_marks


    # Setup the calibration paremeters to adjust for variations between the video and the tracked points
    def calibrate(self, frame_num, pos_to_point_at_name, expected_coord):
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
    def to_tracking_space(self, coord):
        tracked_space_pointed_x = abs(coord[0] - self.origin_screen_x)
        tracked_space_pointed_y = abs(coord[1] - self.origin_screen_y)

        return tracked_space_pointed_x, tracked_space_pointed_y


    # Shows the frame frame_num of the video, in a window named window_name (if provided, otherwise auto generated)
    # And allow the user to click on a point, before returning the coordinates of the click in the screen space
    # The coordinates are returned in tracking data frame
    def point_at(self, frame_num, window_name=None):
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
    def show_frame(self, frame_num, img_name=None, mouse_callback_func=None):
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

            print(x, ' ', y)
            print(self.to_tracking_space((x,y))) 

            # Set the pointed coordinates
            self.pointed_coord = (x,y)

            img = cv2.circle(img, (x,y), radius=0, color=(255, 0, 0), thickness=-1)

            cv2.imshow(img_name, img)


    # Releases the video when the instance is destroyed
    def __del__(self):
        # Release the video when deleting the instance
        if hasattr(self, 'vidcap'):
            self.vidcap.release()
    
