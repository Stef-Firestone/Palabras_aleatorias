# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 09:08:29 2020

@author: stefanie.feuerstein
"""
import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
from tkinter import Tk
from tkinter import ttk
from tkinter import scrolledtext
from PIL import ImageTk, Image
from tkinter import filedialog
from matplotlib.figure import Figure
import matplotlib.image as mpimg 
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import getpass
import glob
import numpy as np
import geopandas as gpd
import rasterio as rio
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep
import io
from django.http import HttpResponse 

class AutoScrollbar(ttk.Scrollbar):  ##scrollbar adapted from: http://effbot.org/zone/tkinter-autoscrollbar.htm
    ''' A scrollbar that hides itself if it's not needed.
        Works only if you use the grid geometry manager '''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with this widget')

    def place(self, **kw):
        raise tk.TclError('Cannot use place with this widget')



        
class Wavy(tk.Frame):
 
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        #create menu bar
        menuBar=tk.Menu(master)
        fileMenu = tk.Menu(master=None, tearoff=False)
        # add cascades and commands
        menuBar.add_cascade(menu = fileMenu, label ='File')
        fileMenu.add_command(label = 'Open', command=self.openDialog)
        fileMenu.add_command(label = 'Exit', command = self.master.destroy)
        
        menuBar.add_cascade(menu = fileMenu, label ='Tools')
        menuBar.add_cascade(menu = fileMenu, label ='Image')
        menuBar.add_cascade(menu = fileMenu, label ='Vector')
        menuBar.add_cascade(menu = fileMenu, label ='Classification')
        menuBar.add_cascade(menu = fileMenu, label ='Menu')

        # configure master window
        master.config(menu=menuBar)
        
        # Vertical and horizontal scrollbars for canvas
        vbar = AutoScrollbar(self.master, orient='vertical')
        hbar = AutoScrollbar(self.master, orient='horizontal')
        vbar.grid(row=1, column=3, rowspan = 3, sticky='ns')
        hbar.grid(row=5, column=1, sticky='we')

        # Create canvas and put image on it
        self.canvas = tk.Canvas(self.master, highlightthickness=0,
                                xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.grid(row=1, column = 1, rowspan = 2, sticky='we')
        self.canvas.config(height = 300, width=100, relief = RIDGE)
        self.canvas.update()  # wait till canvas is created
        vbar.configure(command=self.scroll_y)  # bind scrollbars to the canvas
        hbar.configure(command=self.scroll_x)
        # Make the canvas expandable
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        # Bind events to the Canvas
        self.canvas.bind('<Configure>', self.show_image)  # canvas is resized
        self.canvas.bind('<ButtonPress-1>', self.move_from)
        self.canvas.bind('<B1-Motion>',     self.move_to)
        self.canvas.bind('<MouseWheel>', self.wheel)  # with Windows and MacOS, but not Linux
        self.canvas.bind('<Button-5>',   self.wheel)  # only with Linux, wheel scroll down
        self.canvas.bind('<Button-4>',   self.wheel)  # only with Linux, wheel scroll up
        
        img_arr_def = np.ones(shape=(300, 4000, 3))*255
        self.image =Image.fromarray(img_arr_def,'RGB' )
        self.width, self.height =2000, 2000
        self.imscale = 1  # scale for the canvaas image
        self.delta =2 # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, 2000, 2000, width=0)

        
        # create text window
        self.frame_textwin = ttk.Frame(master)
        self.frame_textwin.grid(row=6, column = 1, rowspan = 2)
        self.frame_textwin.config(height = 400, width=400, relief = RIDGE)
        self.textcomments = scrolledtext.ScrolledText(self.frame_textwin, wrap=tk.WORD)
        self.textcomments.grid(row=3, column = 1, rowspan = 2)
        ttk.Button(self.frame_textwin, text='Clear Window', command=self.clear_text).grid(row=5, column = 1, rowspan = 1, padx=10, pady = 10)
  
    def OpenFile(self, red, green, blue):
        array_stack, self.meta_data = es.stack(self.band_list2, nodata=-9999)
        self.textcomments.insert(END, self.meta_data)
        array_smaller = array_stack[:,1400:2700, 4900:6200]
        fig = plt.figure(dpi = 600)
        ax1 = fig.add_subplot(111)
        ep.plot_rgb(array_smaller, ax = ax1,
            rgb=[red, green, blue],
            stretch=True,
            str_clip=1)
        buf = io.BytesIO()
        canvas = plt.get_current_fig_manager().canvas
        canvas.draw()
        self.image = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())
        #pil_image.save(buf, 'PNG')
        self.width, self.height = self.image.size
        plt.close()   
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.canvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.show_image()     
        

    def show_image(self, event=None):
        ''' Show image on the Canvas '''
        bbox1 = self.canvas.bbox(self.container)  # get image area
        # Remove 1 pixel shift at the sides of the bbox1
        bbox1 = (bbox1[0] + 1, bbox1[1] + 1, bbox1[2] - 1, bbox1[3] - 1)
        bbox2 = (self.canvas.canvasx(0),  # get visible area of the canvas
                 self.canvas.canvasy(0),
                 self.canvas.canvasx(self.canvas.winfo_width()),
                 self.canvas.canvasy(self.canvas.winfo_height()))
        bbox = [min(bbox1[0], bbox2[0]), min(bbox1[1], bbox2[1]),  # get scroll region box
                max(bbox1[2], bbox2[2]), max(bbox1[3], bbox2[3])]
        if bbox[0] == bbox2[0] and bbox[2] == bbox2[2]:  # whole image in the visible area
            bbox[0] = bbox1[0]
            bbox[2] = bbox1[2]
        if bbox[1] == bbox2[1] and bbox[3] == bbox2[3]:  # whole image in the visible area
            bbox[1] = bbox1[1]
            bbox[3] = bbox1[3]
        self.canvas.configure(scrollregion=bbox)  # set scroll region
        x1 = max(bbox2[0] - bbox1[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(bbox2[1] - bbox1[1], 0)
        x2 = min(bbox2[2], bbox1[2]) - bbox1[0]
        y2 = min(bbox2[3], bbox1[3]) - bbox1[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            x = min(int(x2 / self.imscale), self.width)   # sometimes it is larger on 1 pixel...
            y = min(int(y2 / self.imscale), self.height)  # ...and sometimes not
            image = self.image.crop((int(x1 / self.imscale), int(y1 / self.imscale), x, y))
            imagetk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1))))
            imageid = self.canvas.create_image(max(bbox2[0], bbox1[0]), max(bbox2[1], bbox1[1]),
                                               anchor='nw', image=imagetk)
            self.canvas.lower(imageid)  # set image into background
            self.canvas.imagetk = imagetk  # keep an extra reference to prevent garbage-collection
       
       
    def clear_text(self):
        self.textcomments.delete('1.0',END)
    
    ##### definitions for zooming and scrolling in canvas
        
    def scroll_y(self, *args, **kwargs):
        ''' Scroll canvas vertically and redraw the image '''
        self.canvas.yview(*args, **kwargs)  # scroll vertically
        self.show_image()  # redraw the image

    def scroll_x(self, *args, **kwargs):
        ''' Scroll canvas horizontally and redraw the image '''
        self.canvas.xview(*args, **kwargs)  # scroll horizontally
        self.show_image()  # redraw the image

    def move_from(self, event):
        ''' Remember previous coordinates for scrolling with the mouse '''
        self.canvas.scan_mark(event.x, event.y)

    def move_to(self, event):
        ''' Drag (move) canvas to the new position '''
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # redraw the image

    def wheel(self, event):
        ''' Zoom with mouse wheel '''
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        bbox = self.canvas.bbox(self.container)  # get image area
        if bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3]: pass  # Ok! Inside the image
        else: return  # zoom only inside image area
        scale = 1.0
        if event.num == 5 or event.delta == -120:  # scroll down
            i = min(self.width, self.height)
            if int(i * self.imscale) < 30: return  # image is less than 30 pixels
            self.imscale /= self.delta
            scale        /= self.delta
        if event.num == 4 or event.delta == 120:  # scroll up
            i = min(self.canvas.winfo_width(), self.canvas.winfo_height())
            if i < self.imscale: return  # 1 pixel is bigger than the visible area
            self.imscale *= self.delta
            scale        *= self.delta
        self.canvas.scale('all', x, y, scale, scale)  # rescale all canvas objects
        self.show_image()



#OpenFile(tk.Toplevel):
    def openDialog(self):
        self.filedialog = tk.Toplevel(self.master)
        #create widgets
        dir_text = Label(self.filedialog, height = 1, width = 30, text = "Image Directory").grid(row=0, column=0, padx=10, pady=10)
        red_text = Label(self.filedialog, height = 1, width = 30, text = "Red Band").grid(row=1, column=0, padx=10, pady=10)
        green_text = Label(self.filedialog, height = 1, width = 30, text = "Green Band").grid(row=2, column=0, padx=10, pady=10)
        blue_text = Label(self.filedialog, height = 1, width = 30, text = "Blue Band").grid(row=3, column=0, padx=10, pady=10)
        #create field for image directory path:
        dir_path = Entry(self.filedialog, textvariable=0, width = 50).grid(row=0, column = 1, padx=10, pady=10)
        #create drop down menu with image bands in dir_path
        self.band_list = ['select a directory first']
        #red
        self.red_path=StringVar(self.filedialog)
        self.red_path.set(self.band_list[0])
        self.r = OptionMenu(self.filedialog, self.red_path, self.band_list)
        self.r.grid(row=1, column=1, padx=10, pady=10)
        #green
        self.green_path=StringVar(self.filedialog)
        self.green_path.set(self.band_list[0])
        self.g = OptionMenu(self.filedialog, self.green_path, self.band_list)
        self.g.grid(row=2, column=1, padx=10, pady=10)
        #blue
        self.blue_path=StringVar(self.filedialog)
        self.blue_path.set(self.band_list[0])
        self.b = OptionMenu(self.filedialog, self.blue_path, self.band_list)
        self.b.grid(row=3, column=1, padx=10, pady=10)
        #create browse button
        self.dir_button = ttk.Button(self.filedialog, text = 'Select Image Directory', command=lambda:self.OpenImageBand()).grid(row=0, column = 2, padx=10, pady=10)
        loadimages_button = ttk.Button(self.filedialog, text='Load RGB Image', state=DISABLED).grid(row = 4, column=1,columnspan=1, pady=10, sticky='we')

    def OpenImageBand(self):#, band=None):
        user = getpass.getuser()
        #for standard version, uncommend next line
        file = askopenfilename(initialdir='C:/User/%s' % user)
        pathname = StringVar(None)
        pathname.set(self.directory)
        #self.path_name = pathname
        directory_path = Entry(self.filedialog, width = 50,textvariable=pathname).grid(row=0, column = 1, padx=10, pady=10)
        self.band_list2 = glob.glob(self.directory+"/*band*.tif")
        self.band_list = []
        for element in self.band_list2:
            self.band_list.append(element.split("\\")[-1])
        print(self.band_list)
        #self.band_stack, self.meta_data = es.stack(self.band_list2, nodata=-9999)
        #print(band_stack, meta_data)
        #update drop down menus to select file 
        self.r = OptionMenu(self.filedialog, self.red_path, *self.band_list)
        self.r.grid(row=1, column=1, padx=10, pady=10)
        self.g = OptionMenu(self.filedialog, self.green_path, *self.band_list)
        self.g.grid(row=2, column=1, padx=10, pady=10)
        self.b = OptionMenu(self.filedialog, self.blue_path, *self.band_list)
        self.b.grid(row=3, column=1, padx=10, pady=10)
        self.filedialog.attributes('-topmost', True)

        loadimages_button = ttk.Button(self.filedialog, text='Load RGB Image', command = lambda: self.load_images()).grid(row = 4, column=1,columnspan=1, pady=10, sticky='we')
        
    def load_images(self):
        self.red_index = self.band_list.index(self.red_path.get())
        print(self.red_index)
        self.green_index = self.band_list.index(self.green_path.get())
        print(self.green_index)
        self.blue_index = self.band_list.index(self.blue_path.get())
        print(self.blue_index)
        self.filedialog.destroy()
        self.master.attributes('-topmost', True)
        self.OpenFile(self.red_index,self.green_index,self.blue_index)
        
  


def main():

    root = Tk()
    wavy = Wavy(root)
    root.mainloop()


if __name__=="__main__":main()       
