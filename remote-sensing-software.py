# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 10:22:39 2020

@author: stefanie.feuerstein
"""

import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import Tk
from tkinter import ttk
from tkinter import scrolledtext
from PIL import ImageTk, Image
from tkinter import filedialog

import matplotlib.image as mpimg 
import matplotlib.pyplot as plt 


# Defs

def clear_window():
    action.configure(text='window cleared')

def OpenFile():
    name = askopenfilename(initialdir="C:/python_workspace/WaVy/",
                           filetypes =(('Image file',"*.png"),("All Files","*.*")),
                           title = "Choose a file."
                           )
    print (name)
    #img = mpimg.imread(str(name),0)
    #plt.imshow(img)
    toprow = tk.Frame(win)
    img = ImageTk.PhotoImage(Image.open(str(name)))
    globeview = tk.Label(toprow, image = img)
    globeview.pack(side = "top") # the side argument sets this to pack in a row rather than a column
    toprow.pack()   

    
   

    #Using try in case user types in unknown file or closes without choosing a file.
#    try:
#        with open(name,'r') as UseFile:
#            print(UseFile.read())
#    except:
#        print("No file exists")
   

##### STEP 1: Create GUI with needed widgets
root = Tk()
#root.withdraw()

# create GUI
win = tk.Toplevel()
win.title('Steffis-Wavy - Remote Sensing Software')
win.geometry("400x400")

#create frames:
#toprow = tk.Frame(win)


# Creating a Menu Bar
menuBar = tk.Menu(win)
win.config(menu=menuBar)

# Add menu items
fileMenu = tk.Menu(menuBar, tearoff=0)
fileMenu.add_command(label="Open", command=OpenFile)

fileMenu.add_command(label = 'Exit', command = lambda:exit())
menuBar.add_cascade(label="File", menu=fileMenu)

toolsMenu = tk.Menu(menuBar, tearoff=0)
#toolsMenu.add_command(label="Open")
menuBar.add_cascade(label="Tools", menu=toolsMenu)

imageMenu = tk.Menu(menuBar, tearoff=0)
#imageMenu.add_command(label="Open")
menuBar.add_cascade(label="Image", menu=imageMenu)

vectorMenu = tk.Menu(menuBar, tearoff=0)
#vectorMenu.add_command(label="Open")
menuBar.add_cascade(label="Vector", menu=vectorMenu)

classificationMenu = tk.Menu(menuBar, tearoff=0)
#classificationMenu.add_command(label="Open")
menuBar.add_cascade(label="Classification", menu=classificationMenu)

helpMenu = tk.Menu(menuBar, tearoff=0)
#helpMenu.add_command(label="Open")
menuBar.add_cascade(label="Help", menu=helpMenu)


# add image window

#Import image 
#pic1 = 'C:/python_workspace/WaVy/test_image.png'
#### noch gdal ersetzen zum Laden von images
#img1 = ImageTk.PhotoImage(Image.open(pic1))
#img1 = ImageTk.PhotoImage(Image.open(name))
#globeview = tk.Label(toprow, image = img)
#globeview.pack(side = "top") # the side argument sets this to pack in a row rather than a column
#toprow.pack() # pack the toprow

# Using a scrolled Text control
scrolW  = 30; scrolH  =  3
scr = scrolledtext.ScrolledText(win, width=scrolW, height=scrolH, wrap=tk.WORD)
scr.pack(expand=True)
scr.grid(column=0, sticky='WE', columnspan=3)


# add clear window-button
action = ttk.Button(win, text="Clear Window", command=clear_window)
action.pack(side = "bottom") 
action.pack() # pack the toprow


############### Step 2: add functionality






win.mainloop()