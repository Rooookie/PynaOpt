#-*- encoding=UTF-8 -*-
__author__ = 'Yisu Nie'

# Debug
import pdb 

# Import numpy
import sys
import os
import matplotlib
import pandas as pd
import ConfigParser as cp

# Use Tkinter for python 2, tkinter for python 3
if sys.version_info[0] < 3:
    import Tkinter as Tk 
else:
    import tkinter as Tk

# Import file dialog module
import tkFileDialog

# Import my modules
from tkdialog import * 

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from PIL import Image, ImageTk 

# colors for plots

    
__colors__ = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

__configs__ = cp.ConfigParser()

__extopen__ = {"nt": "start ",
                "posix": "open "}

def ext_open(fname):
    try:
        os.system(__extopen__[os.name] + fname) 
    except KeyError:
        pass

class PlotItem(pd.DataFrame):
    """Data to generate plots with matplotlib
    Subclass of pandas.DataFrame
    """
    def __init__(self, parent=None, *args, **kwargs):
        """A plot record as pandas DataFrame
        """
        pd.DataFrame.__init__(self, parent, *args, **kwargs)

    def normalized_data(self):
        """Scale data to [0,1]
        Reutrn scaled data frame
        """
        data_frame = self.copy()
        for index, column in enumerate(data_frame, start=0):
            if data_frame.max()[index] == data_frame.min()[index]:
                data_frame[column] = 0.5
            else:
                data_frame[column] = (data_frame[column] - data_frame.min()[index])/(data_frame.max()[index] - data_frame.min()[index])
        return data_frame

    @classmethod
    def read_csv(cls, *args, **kwargs):
        data_frame = pd.read_csv(*args, **kwargs)
        data_frame.__class__ = PlotItem
        return data_frame
    
class MainFrame(Tk.Frame):
    """Main Frame for the application
    Subclass of Tk.Frame
    """
    def __init__(self, parent=None, *args, **kwargs):
        self.parent = parent
        Tk.Frame.__init__(self, parent, *args, **kwargs)
        self.monitor_button = Tk.Button(self.parent, text='Data Ponitor', width=25, command=self.new_monitor)
        self.monitor_button.pack()
        
    def new_monitor(self):
        self.new_window = Tk.Toplevel(self.parent)
        self.monitor = DataMonitor(self.new_window)
                    
class DataMonitor(Tk.Frame):
    """Frame to hold data visualization using Tkinter
    as a subclass
    """
    item_plot_flag = []
    
    def __init__(self, parent=None, *args, **kwargs):
        """
        """
        Tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.confirm = True;

        self._construct_menubar()
        self._construct_canvas()
        self._construct_toolbar()
        self._construct_minibuffer()
        
    def _construct_menubar(self):
        """
        """
        self.menubar = Tk.Menu(self.parent, tearoff=0)
        self.parent.config(menu=self.menubar)

        file_menu = Tk.Menu(self.menubar)
        file_menu.add_command(label="Open", command=self.load_data_file)
        file_menu.add_command(label="Quit", command=self.quit)
        
        self.menubar.add_cascade(label="File", menu=file_menu)

    def _construct_canvas(self):
        """
        """
        self.figure = Figure(figsize=(8,6), dpi=100, facecolor='white')
        self.canvas = FigureCanvasTkAgg(self.figure, self.parent)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky='n')

        #        self.canvas._tkcanvas.config(background='white', borderwidth=0,
        #        highlightthickness=0)

    def _construct_toolbar(self):
        """
        """
        self.toolbar = ToolBar(self.parent)
        self.toolbar.grid(row=0, column=0, sticky='w')
        # Matplotlib toolbar
        toolbar = NavigationToolbar2TkAgg(self.canvas, self.toolbar)
        toolbar.update()
        # Load button
        # _image_load = ImageTk.PhotoImage(Image.open(os.getcwd()+'/images/LoadIcon.png'))
        # _button_load = Tk.Button(self.toolbar, image=_image_load, command=self.load_data_file)
        button_load = Tk.Button(self.toolbar, text='Load',
        command=self.load_data_file)
        self.button_reload = Tk.Button(self.toolbar, text='Reload',
        command=self.reload_plot, state='disabled')

        button_load.pack(side='left',fill='both')
        self.button_reload.pack(side='left',fill='both')
        toolbar.pack(side='left',anchor='w',after=self.button_reload)
        
    def _construct_minibuffer(self):
        """
        """
        self.minibuffer = MiniBuffer(self.parent)
        self.minibuffer.grid(row=2,column=0,columnspan=2)
            
    def quit(self):
        self.parent.quit()
        self.parent.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate    

    def generate_plot(self):
        """
        """
        self.checkbar = CheckBar(self.plot_item, self.refresh_plot, parent=self.parent)
        self.checkbar.grid(row=1, column=1, sticky='n')
        self.refresh_plot()

    def refresh_plot(self):
        """
        """
        matplotlib.rc('lines', linewidth=2)
        matplotlib.rc('grid', color='0.5', linestyle='--', linewidth=0.5)  # solid gray grid lines
        matplotlib.rc('xtick.major', size=4)
        matplotlib.rc('ytick.major', size=4)
        item_plot_flag = self.checkbar.state()   # update plot status
        subplot = self.figure.add_subplot(1,1,1)
        subplot.clear()
        if item_plot_flag[-1]:
            my_item = self.plot_item.normalized_data()
        else:
            my_item = self.plot_item
        for index, column in enumerate(my_item, start=0):   # iterate over columns
            if item_plot_flag[index]:
                subplot.plot(my_item.index, my_item[column],
                              color=__colors__[index])
        subplot.grid(True)
        self.figure.canvas.show()
        
    def load_data_file(self):
        """
        """
        try:
            self.file_name = tkFileDialog.askopenfilename(initialdir=os.getcwd(), title='Load data')
            self.minibuffer.mini_message("Load result data from " + self.file_name)
        except (UnboundLocalError, IOError) as error:
            self.minibuffer.mini_message("Data file not found!")
        if self.file_name:
            YsDialog(self.file_name, self)
            if self.confirm:
                self.button_reload.configure(state='normal')
                self.button_reload.update()
                self.plot_item = self.read_file(self.file_name)
                self.generate_plot()
            
    def reload_plot(self):
        """
        """
        self.read_file(self.file_name)
        self.refresh_plot()
        
    def read_file(self, fname, ext=None):
        """
        """
        if not ext:
            _, ext = os.path.splitext(fname)

        header = __configs__.getint('DataMonitor','header')
        skiprows = __configs__.get('DataMonitor','skiprows')
        index_col = __configs__.getint('DataMonitor','index_col')
        is_list = __configs__.getboolean('DataMonitor','is_list')
        if is_list:                       # if_list is true, return a list 
            skiprows = [int(num) for num in skiprows.split(',')]
        else:                             # if_list if false, return an integer
            skiprows = int(skiprows)

        if ext == '.csv': 
            plot_item = PlotItem.read_csv(fname, header=header,
        skiprows=skiprows, index_col=index_col)            
        elif ext == '.xls':
            pass                

        return plot_item

    
class CheckBar(Tk.Frame):
    """An array of CheckButtons for column-wise switches of the plotted
    dataframe. Input arguments:
    PlotItem: data frame to be visualized
    callback: callback function
    """
    def __init__(self, PlotItem, callback, parent=None, side='top', anchor='w'):
        Tk.Frame.__init__(self, parent)
        label = Tk.Label(self, text='Entries')
        label.pack(side='top', anchor='center')
        self.values = []
        for index, pick in enumerate(PlotItem.columns, start=0):
            value = Tk.BooleanVar()
            value.set(1)                  # defult value as checked
            check = Tk.Checkbutton(self, text=pick, width=18,
                                    bg=__colors__[index], variable=value,
                                   anchor='w', justify='left', 
                                   command=callback)
            check.pack(side=side, anchor=anchor, expand='no')
            self.values.append(value)
        value_normalized = Tk.BooleanVar()
        check_normalized = Tk.Checkbutton(self, text='Scaled [0,1]', variable=value_normalized, justify='left',command=callback)
        check_normalized.pack(side=side, anchor=anchor, expand='no')
        self.values.append(value_normalized)
        
        
    def state(self):
        return map((lambda value: value.get()), self.values)

class ToolBar(Tk.Frame):
    """
    """
    def __init__(self, parent=None, *args, **kwargs):
        Tk.Frame.__init__(self, parent, *args, **kwargs)
        
class MiniBuffer(Tk.Frame):
    """
    """
    def __init__(self, parent=None):
        Tk.Frame.__init__(self, parent)
        self.strvar = Tk.StringVar()
        self.strvar.set('Welcome to PynaOpt')
        self.message = Tk.Label(self, textvariable=self.strvar, justify='l', fg='red', bg='yellow')
        self.message.pack(side='bottom', fill='y', expand='yes', anchor='w')
        
    def mini_message(self, message):
        self.strvar.set(message)

class YsDialog(Dialog):

    def __init__(self, fname, parent=None):
        self.file_name = fname
        Dialog.__init__(self, parent)

    def construct_body(self):

        box = Tk.Frame(self)
        box.pack()
        
        self.has_header = Tk.StringVar()
        self.is_list = Tk.StringVar()     # ConfigParser - full functionality (including interpolation and output to files) can only be achieved using string values
        
        Tk.Label(box, text="Header row:").grid(row=0)
        Tk.Label(box, text="Skip rows:").grid(row=1)
        Tk.Label(box, text="Index column:").grid(row=2)
        Tk.Button(box, text="Check file", command=lambda: ext_open(self.file_name)).grid(row=0, column=3)
        self.entry1 = Tk.Entry(box)
        self.entry2 = Tk.Entry(box)
        self.entry3 = Tk.Entry(box)

        # provide default values from last saved options
        try:
            self.entry1.insert(0, __configs__.get('DataMonitor','header'))
            self.entry2.insert(0, __configs__.get('DataMonitor','skiprows'))
            self.entry3.insert(0, __configs__.get('DataMonitor','index_col'))
            self.is_list.set(__configs__.getint('DataMonitor','is_list'))
            self.has_header.set(__configs__.getint('DataMonitor','has_header'))
        except (cp.NoSectionError, cp.NoOptionError):
            pass
        
        self.entry1.grid(row=0, column=1)
        self.entry2.grid(row=1, column=1)
        self.entry3.grid(row=2, column=1)

        Tk.Checkbutton(box, text='header',
        variable=self.has_header, command=lambda: YsDialog.naccheck(self.entry1,self.has_header)).grid(row=0, column=2, sticky='w')
        Tk.Checkbutton(box, text='list', variable=self.is_list).grid(row=1,
        column=2, sticky='w')
        
        return self.entry1 # initial focus

    def apply(self):
        
        if not __configs__.has_section('DataMonitor'):
            __configs__.add_section('DataMonitor')
        __configs__.set('DataMonitor','header', self.entry1.get())
        __configs__.set('DataMonitor','skiprows', self.entry2.get())
        __configs__.set('DataMonitor','index_col', self.entry3.get())
        __configs__.set('DataMonitor','is_list', self.is_list.get())
        __configs__.set('DataMonitor','has_header', self.has_header.get())
        __configs__.write(open("option.ini", "w"))

    @staticmethod
    def naccheck(entry, var):
        if int(var.get()):
            entry.configure(state='normal')
        else:       
            entry.configure(state='disabled')
        entry.update()


def main():
#    matplotlib.use('TkAgg')
    __configs__.read('option.ini')
    root = Tk.Tk()
    root.title('PynaOpt Dynamic Optimization Toolbox')
    root.grid_rowconfigure(0,weight=1) 
    root.grid_columnconfigure(0,weight=1) 
    app = MainFrame(parent=root)
    app.lift()
    app.mainloop()
    

 
if __name__ == '__main__':
    main()
    
"""
__colors__ = [(0.12,0.46,0.70), (1.00,0.50,0.05), (0.17,0.63,0.17), 
              (0.84,0.15,0.16), (0.58,0.40,0.74), (0.55,0.33,0.29), 
              (0.89,0.47,0.76), (0.50,0.50,0.50), (0.73,0.74,0.13),
              (0.09,0.74,0.81)]

              __hex_colors__ = ['#%02x%02x%02x'%color for color in __colors__]
              
            def on_key_event(event):
        print('you pressed %s'%event.key)
        key_press_handler(event, canvas, toolbar)

        canvas.mpl_connect('key_press_event', on_key_event)

                item_plot_flag = [1]*PlotItem.count_item

command=lambd :callback(PlotItem)
with open(_file_name,'rU') as file:	# use file to refer to the file object
_headers = file.readline().rstrip('\n').split(',')
_headers = [name.strip('"').strip() for name in _headers]

#    data = np.genfromtxt('result.csv', skip_header=2, delimiter=',')
#    with open("result.csv",'rU') as file:	# Use file to refer to the file object
#        headers = file.readline().rstrip('\n').split(',')
#    myplot = PlotItem(headers[1:], data[:,0], np.delete(data,0,1))
#    myplot = load_data_file()

#    app.generate_plot(myplot)

"""

