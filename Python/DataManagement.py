# -*- coding: utf-8 -*-
"""
Created on Sun Mar  3 17:03:31 2024

@author: walid
"""

from GUI import GUI
import os
import csv

filetypes = (('CSV', '*.csv'),('All files', '*.*'))
data_ext = [".csv",".txt"]
x_col_name = "x"
y_col_name = "y"
likelihood_col_name = "likelihood"

class BodyPart:
    def __init__(self, bodypart_name):
        self.name = bodypart_name
        self.x = []
        self.y = []
        self.likelihood = []

class TrackingData:
    def __init__(self, data_name, file_path=None, data_delimiter=',', bodypart_row_name="bodyparts", coord_row_name="coords"):
        # Ask to pick a path if none is given
        if file_path is None:
            ui = GUI()
            file_path = ui.ask_data_file(data_name, initial_dir='.', filetypes=filetypes)
        
        # Check that the file exists
        if file_path == "" or not os.path.exists(file_path):
            raise FileNotFoundError("Error : '" + file_path + "' is not a valid file path")
        
        # Save the file parameters in the object
        self.file_path = file_path
        self.name = data_name
        self.data = dict()

        # Extract the directory, name and extension of the file
        basename = os.path.basename(file_path)
        self.file_name, self.file_ext = os.path.splitext(basename)
        self.file_dir = os.path.dirname(file_path)

        # Check that the file extension is valid
        if self.file_ext not in data_ext:
            raise Exception("Error : '" + self.file_ext + "' is not a valid data extension")

        # Open the data file and extract the data
        with open(self.file_path, mode='r') as data_file:
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
                        if row[i] == x_col_name:
                            x_col.append(i)
                        elif row[i] == y_col_name:
                            y_col.append(i)
                        elif row[i] == likelihood_col_name:
                            likelihood_col.append(i)
                        else:
                            raise Exception("Error in row '" + coord_row_name + "' : '" + row[i] + "' at column " + i + " is not a valid column name")
                
                # If the value is an integer (ie is a frame number)
                elif row[0].isdigit():
                    for i in x_col:
                        bodypart = all_bodyparts[i]
                        self.data[bodypart].x.append(row[i])
                    
                    for i in y_col:
                        bodypart = all_bodyparts[i]
                        self.data[bodypart].y.append(row[i])
                    
                    for i in likelihood_col:
                        bodypart = all_bodyparts[i]
                        self.data[bodypart].likelihood.append(row[i])
        

