import tkinter as tk
from tkinter import filedialog as fd

# Metaclass for a Singleton
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# Singleton class managing the windows shown to the user from tkinter 
#   (ask for finding a file,...)
class GUI(metaclass=Singleton):
    def __init__(self):
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', True)

    def ask_data_file(self, data_name:str, filetypes, initial_dir:str='.'):
        file_path = fd.askopenfilename(title = data_name, initialdir=initial_dir, filetypes=filetypes)

        return file_path