# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 17:03:31 2024

@author: walid
"""

from GUI import GUI
import os
import csv
import cv2


class DataFileException(Exception):
    """Raise for errors when attempting to read a data file"""



# Base class for opening data files
class Data:
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
    def __init__(self, bodypart_name):
        self.name = bodypart_name
        self.x = []
        self.y = []
        self.likelihood = []

    # Returns the coordinates (x,y) of the tracked body part at frame frame_num
    def get_coord_at_frame(self, frame_num):
        return (self.x[frame_num], self.y[frame_num])

    # Print on the command line the data contained in the limb at frame frame_num
    def print_data_at_frame(self, frame_num):
        print(f"({self.x[frame_num]}, {self.y[frame_num]}) - {self.likelihood[frame_num]}")



# Class managing the tracking data
class TrackingData(Data):
    # File types allowed when asking the user to pick the data file
    filetypes = (('CSV', '*.csv'),('All files', '*.*'))
    # Initial directory when asking the user to pick the data file
    initial_dir = '.'
    # Extensions allowed for a data file
    data_ext = [".csv",".txt"]

    # Name of the corresponding columns
    x_col_name = "x"
    y_col_name = "y"
    likelihood_col_name = "likelihood"

    def __init__(self, data_name, file_path=None, data_delimiter=',', bodypart_row_name="bodyparts", coord_row_name="coords"):
        # Get the data from the file
        super().__init__(data_name, file_path, initial_dir=self.initial_dir, file_types=self.filetypes, data_ext=self.data_ext)

        # Create the tracking data dictionnary
        self.data = dict()

        # Open the data file and extract the data
        with open(self.file_path, mode="r") as data_file:
            csv_reader = csv.reader(data_file, delimiter=data_delimiter)

            # Temporary values
            all_bodyparts = [""]
            x_col = []
            y_col = []
            likelihood_col = []

            # Read each row of the data file
            for row in csv_reader:
                # If it's the bodyparts row, create the bodyparts in the data dictionnary
                if row[0] == bodypart_row_name:
                    for bodypart in row[1:]:
                        self.data[bodypart] = BodyPart(bodypart)
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
                        self.data[bodypart].x.append(float(row[i]))
                    
                    for i in y_col:
                        bodypart = all_bodyparts[i]
                        self.data[bodypart].y.append(float(row[i]))
                    
                    for i in likelihood_col:
                        bodypart = all_bodyparts[i]
                        self.data[bodypart].likelihood.append(float(row[i]))

    # Get the time variables
    def get_time(self, sampling):
        key = next(iter(self.data))
        frames = len(self.data[key].x)
        total_time = frames / sampling

        return frames, total_time

    # Converting the data to bottom right origin
    def convert_origin(self, cf):
        key = next(iter(self.data))
        x_max = self.data[key].x[0]
        y_max = self.data[key].x[0]

        for part in self.data:
            temp = max([x for x in self.data[part].x])
            if temp > x_max:
                x_max = temp

            temp = max([y for y in self.data[part].y])
            if temp > y_max:
                y_max = temp

        for part in self.data:
            self.data[part].x = [(x_max - x) / cf for x in self.data[part].x]
            self.data[part].y = [(y_max - y) / cf for y in self.data[part].y]



# Class managing video data
class VideoData(Data):
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
        self.calibration_factor_x = 1
        self.calibration_factor_y = 1
        self.origin_screen_x = 0
        self.origin_screen_y = 0
        self.origin_tracking_x = 0
        self.origin_tracking_y = 0


    # Setup the calibration factors to adjust for variations between the video and the tracked points
    def calibrate(self, frame_num, 
                  pos1_to_point_at_name, expected_coord_1,
                  pos2_to_point_at_name, expected_coord_2):
        
        # Reset the calibration parameters
        self.calibration_factor_x = 1
        self.calibration_factor_y = 1
        self.origin_screen_x = 0
        self.origin_screen_y = 0
        self.origin_tracking_x = 0
        self.origin_tracking_y = 0

        # Point the first coordinates
        pointed_x1, pointed_y1 = self.point_at(frame_num, window_name="Point at " + pos1_to_point_at_name)

        # Point the second coordinates
        pointed_x2, pointed_y2 = self.point_at(frame_num, window_name="Point at " + pos2_to_point_at_name)

        # Calculate the transformation from tracking data screen coordinates to current video screen coordinates
        expected_x1, expected_y1 = expected_coord_1
        expected_x2, expected_y2 = expected_coord_2

        # Moving 1 unit along x on the video corresponds to moving calibration_factor_x units on the tracking data
        self.calibration_factor_x = (expected_x2 - expected_x1) / (pointed_x2 - pointed_x1)
        self.calibration_factor_y = (expected_y2 - expected_y1) / (pointed_y2 - pointed_y1)

        # Determine a random origin point
        self.origin_screen_x = pointed_x1
        self.origin_screen_y = pointed_y1
        self.origin_tracking_x = expected_x1
        self.origin_tracking_y = expected_y1


    # Converts the coordinates from screen space to tracking data space (ie with the same origin,... as the tracking data)
    def to_tracking_space(self, coord):
        tracked_space_pointed_x = self.origin_tracking_x + self.calibration_factor_x * (coord[0] - self.origin_screen_x)
        tracked_space_pointed_y = self.origin_tracking_y + self.calibration_factor_y * (coord[1] - self.origin_screen_y)

        return tracked_space_pointed_x, tracked_space_pointed_y


    # Shows the frame frame_num of the video, in a window named window_name (if provided, otherwise auto generated)
    # And allow the user to click on a point, before returning the coordinates of the click in the screen space
    def point_at(self, frame_num, window_name=None):
        # Reset the pointed coordinates value and last key pressed
        self.pointed_coord = None
        key_pressed = None

        # While there is no pointed coordinates AND the user didn't close the window
        while self.pointed_coord is None and key_pressed != -1:
            key_pressed = self.show_frame(frame_num, img_name=window_name, mouse_callback_func=self.__get_point_click_event)

        # If the user closed the window without pointing, exit the program
        if self.pointed_coord == None:
            exit()

        return self.pointed_coord
    

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

    # get the time variables
    def get_time(self, sampling):
        frames = len(self.data["head"].x)
        time = frames / sampling

        return frames, time

    # converting to bottom right origin
    def conversion(self, cf):
        x_max = float(self.data["head"].x[0])
        y_max = float(self.data["head"].x[0])

        for part in self.data:
            temp = max([float(x) for x in self.data[part].x])
            if temp > x_max:
                x_max = temp

            temp = max([float(y) for y in self.data[part].y])
            if temp > y_max:
                y_max = temp

        for part in self.data:
            self.data[part].x = [(x_max - float(x)) / cf for x in self.data[part].x]
            self.data[part].y = [(y_max - float(y)) / cf for y in self.data[part].y]
