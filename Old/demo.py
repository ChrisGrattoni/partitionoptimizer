# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/	

import tkinter as tk # used in the GUI
from tkinter import filedialog # used for the GUI file browser
from tkinter import font # used to set the width of the "Start" button

# default width of the GUI window
WINDOW_WIDTH = 600



class Window(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Student Partition Optimization Tool for Schools")
      
        self.grid_columnconfigure(7, weight=1)
        
        self.geometry(str(WINDOW_WIDTH) + 'x400') 
        
        self.frames = {}

        for F in (StartPage, PageOne):

            frame = F(self, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
     
        self.input_dict = {} 
        
        main_label = tk.Label(self, text = "Student Partition Optimization Tool for Schools", font = ('bold', 18), padx = 10, pady = 10)
        
        main_label.grid(sticky = "W", row = 0, column = 0, columnspan = 2)
        
        self.text_input("Partition Size (2 or 4)", 4, 1)
        
        self.text_input("Max Class Size (2 Groups)", 15, 2)
        
        self.text_input("Max Class Size (4 Groups)", 9, 3)
        
        self.file_selector("Student Course Data:", 4)

        self.file_selector("Required Student Subgroups:", 6)

        self.file_selector("Preferred Student Subgroups:", 8)

        self.text_input("Max Runtime (Minutes)", 480, 10)

        button = tk.Button(self, text = "Start Partition Optimizer",
                            command = lambda: controller.show_frame(PageOne), width = WINDOW_WIDTH//tk.font.Font().measure(0))
        button.grid(row = 11, column = 0, columnspan = 2, sticky="NSEW")

    def text_input(self, label_text, default_value, starting_row):
        text = tk.StringVar(self)
        text.set(default_value)
        label = tk.Label(self, text = label_text, font = ('bold', 12), padx = 10, pady = 10)
        label.grid(sticky = "W", row = starting_row, column = 0)
        entry = tk.Entry(self, textvariable = text)
        self.input_dict[label_text] = entry
        entry.grid(row = starting_row, column = 1)

    def file_selector(self, label_text, starting_row):
        label = tk.Label(self, text = label_text, font = ('bold', 12), padx = 10)
        label.grid(sticky = "W", row = starting_row, column = 0)

        button_frame = tk.Frame(self)
        button_frame.grid(row = starting_row, column = 1)

        button = tk.Button(button_frame, text = "Browse", command = lambda: self.fileDialog(location_label))
        button.grid(row = starting_row, column = 1)
        button = tk.Button(button_frame, text = "Clear", command = lambda: self.clear(location_label))
        button.grid(row = starting_row, column = 2)

        location_label = tk.Label(self, text = "", width = WINDOW_WIDTH//tk.font.Font().measure(0))
        self.input_dict[label_text] = location_label
        location_label.grid(row = starting_row + 1, column = 0, columnspan = 2)

    def fileDialog(self, label):
        filename = tk.filedialog.askopenfilename(initialdir =  "IO_DIRECTORY", title = "Select A File", filetype = (("csv","*.csv"),("all files","*.*")) )
        label.configure(text = filename)

    def clear(self, label):
        label.configure(text="")


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        main_label = tk.Label(self, text = "Running Genetic Algorithm", font = ('bold', 18), padx = 10, pady = 10)
        main_label.grid(row = 0, column = 0)
        


root = Window()
root.mainloop()