
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib import backend_bases
# mpl.rcParams['toolbar'] = 'None'
from design import design_scheme
import matplotlib as mpl
from session_cache import session_cache, current_reference_spectrum
from additionals import on_enter, on_leave

mpl.rcParams['text.color'] = "#D9D9D9"
mpl.rcParams['axes.labelcolor'] = "#D9D9D9"
mpl.rcParams['xtick.color'] = "#D9D9D9"
mpl.rcParams['ytick.color'] = "#D9D9D9"





class GraphWidget(tk.Frame):

    def __init__(self, parent, type, enlarged = None):
        super().__init__()

        self.parent = parent
        self.type = type
        self.enlarged = enlarged
        self.fit_param_names = ['PUIII', 'PUIV', 'PUV', 'PUVI', 'PUColl']
        self.fit_graph_configurations = [["original data","solid"], ["fitted data","dashed"], ["residuum","dashed"]]
        self.fig, self.ax = plt.subplots()
        self.cursor = None
        self.plot_designation = ["Titel", "x_axis_name", "y_axis_name"]
        self.figsize = [5.2, 2.5]
        self.frame = tk.Frame(self.parent, background=design_scheme.bg_color,highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd= 0)
        self.frame.grid(row=1, column=1, padx=5, pady=10)
        self.frame.propagate(0)
        self.toolbar_width = 300
        self.initTypeDependingValues()
        self.initToolbar()
        self.plot()
        self.addToolbarLabelAndBtn()




    def initTypeDependingValues(self):
        if self.type == "fit":
            self.initFitValues()
        if self.type == "fit results":
            self.initResultsValues()
        if self.type == "jump":
            self.initJumpValues()
        if self.type == "reference spectrum":
            self.initRefSpectraValues()
        if self.type == "baseline":
            self.initBaselineValues()
        if self.enlarged != None:
            self.figsize = [13.5, 6.5]
            if self.type == "fit":
                self.toolbar_width = 420

    def initFitValues(self):
        self.plot_designation = ["Spectrum Analyse", "Wavelength [nm]", "Absorbtion"]
        #self.toolbar_width = 300

    def initResultsValues(self):
        self.plot_designation = ["Spectrum Ratios", "Type", "Ratio"]
        self.toolbar_width = 40

    def initJumpValues(self):
        self.plot_designation = ["Spectrum", "Wavelength [nm]", "Absorbtion"]
        #self.figsize = [7.5, 4.5]
        self.toolbar_width = 350

    def initRefSpectraValues(self):
        if current_reference_spectrum.id == -1:
            self.plot_designation = ["Spectrum", "Wavelength [nm]", "Absorbtion"]
        else:
            self.plot_designation = [f"{current_reference_spectrum.type} Spectrum in {current_reference_spectrum.solution}", "Wavelength [nm]", "Absorbtion"]
        self.toolbar_width = 200

    def initBaselineValues(self):
        self.plot_designation = ["Spectrum Analyse", "Wavelength [nm]", "Absorbtion"]
        self.toolbar_width = 350

    def plot(self):
        if self.type == "fit":
            self.plotData([session_cache.original_data, session_cache.fitted_data, session_cache.fitted_data_residuum], [])
        if self.type == "fit results":
            self.plotData([session_cache.fitted_params],[])
        if self.type == "jump":
            self.plotData([session_cache.original_data_wo_jumps_baseline, session_cache.current_jump[2]], [])
        if self.type == "reference spectrum":
            self.plotData([current_reference_spectrum.referencespectra_measurements],[])
        if self.type == "baseline":
            self.plotData([session_cache.original_data_wo_baseline,session_cache.current_offset[0],session_cache.current_offset[1]],[])

    def plotData(self, data_list,line_list):
        plt.close(self.fig)
        self.calcPlot(data_list,line_list)
        self.adjustAppearance()

        canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=20, column=1, padx=10, pady=20, columnspan=4, rowspan=1)

        self.addToolbar(canvas)

        cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        if self.type != "fit" and self.type != "baseline":
            self.fig.canvas.mpl_disconnect(cid)
        else:
            self.cursor = Cursor(self.ax, horizOn=False, vertOn=True, useblit=True, color='black', linewidth=1)
            if self.enlarged or self.type == "baseline":
                self.cursor = Cursor(self.ax, horizOn=True, vertOn=True, useblit=True, color='black', linewidth=1)

        plt.close(self.fig)

    def calcPlot(self, data_list,line_list):

        self.fig, self.ax = plt.subplots()

        i = 0
        for element in data_list:
            if self.type == "fit results":
                self.ax.bar(self.fit_param_names,[x[1] for x in element], color= design_scheme.color_scheme_graph[i])
            else:
                self.ax.plot([x[0] for x in element],[x[1] for x in element], color= design_scheme.color_scheme_graph[i], label=self.fit_graph_configurations[i][0], linestyle=self.fit_graph_configurations[i][1])
            i += 1

        if self.type == "fit":
            self.plotOmittedAreas()
            self.ax.legend(facecolor= design_scheme.bg_color, fontsize=10)


        i = 0
        for lines in line_list:
            self.ax.axvline(x=lines, color='red', linestyle='--')
            i += 1
        self.ax.axhline(y=0, color='k', linewidth=0.5)

    def plotOmittedAreas(self):
        i = 0
        #print(session_cache.omitted_areas)
        for area in session_cache.omitted_areas:
            if area[2]:
                x = []
                y = []
                for element in session_cache.original_data:
                    if element[0] >= area[0] and element[0] <= area[1]:
                        x.append(element[0])
                        y.append(element[1])
                self.ax.plot(x,y, color="red", label=f"omitted area {i + 1}")
            i += 1

    def onclick(self, event):
        if event.xdata != None and self.enlarged == None:
            if self.type == "fit":
                session_cache.graphvalue = round(event.xdata, 2)
                self.graph_value_label.config(text=f'{round(event.xdata, 2)}')
            if self.type == "baseline":
                session_cache.graphvalue_baseline = [event.xdata,event.ydata]
                self.graph_value_label.config(text=f'({round(event.xdata, 2)},{round(event.ydata, 3)})')



    def fitFormatCoord(self,x, y):
        if self.enlarged or self.type == "baseline":
            return f'x = {x:.2f} , y = {y:.2f}'
        return f'x = %.2f' % x

    def emptyFormatCoord(self,x, y):
        return ''

    def adjustAppearance(self):
        self.fig.patch.set_facecolor('#595959')
        self.ax.set_facecolor('#3A3A3C')
        #self.fig.patch.set_facecolor(design_scheme.bg_color)
        #self.ax.set_facecolor(design_scheme.bg_optionmenu)
        self.ax.set_title(self.plot_designation[0])
        self.ax.set_xlabel(self.plot_designation[1])
        self.ax.set_ylabel(self.plot_designation[2])
        if self.type == "fit" or self.type == "baseline":
            self.ax.format_coord = self.fitFormatCoord
        else:
            self.ax.format_coord = self.emptyFormatCoord
        self.fig.set_size_inches(self.figsize[0], self.figsize[1], forward=True)
        self.fig.tight_layout()

        #self.ax.legend()

    def addLegend(self):
        pass

    def addToolbar(self,canvas):

        toolbarFrame = tk.Frame(master=self.frame,width = self.toolbar_width, height = 40, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color_child, highlightthickness=design_scheme.h_thickness_child, bd=0)
        toolbarFrame.grid(row=21, column=1, padx=5, pady=5, columnspan=1, rowspan=1, sticky="W")
        toolbarFrame.propagate(0)
        toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)
        toolbar.config(background=design_scheme.bg_color)
        toolbar._message_label.config(foreground=design_scheme.font_color)
        for button in toolbar.winfo_children():
            button.config(background=design_scheme.bg_color, highlightbackground=design_scheme.border_color_child, highlightthickness=design_scheme.h_thickness_child, bd=0, relief=design_scheme.btn_relief)
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
        toolbar.update()


    def addToolbarLabelAndBtn(self):
        if self.enlarged == None and self.type != "jump":
            self.button = ttk.Button(self.frame, text="expand", command=self.expandGraph)
            self.button.grid(column=3, row=21, padx=0, pady=0, columnspan=1, rowspan=1)
            if self.type == "fit":
                self.graph_value_label = ttk.Label(self.frame, text=f"N.A.", width=8)
                self.graph_value_label.grid(column=2, row=21, padx=0, pady=5, columnspan=1, rowspan=1)
            if self.type == "baseline":
                self.graph_value_label = ttk.Label(self.frame, text="choosen point:", width=15)
                self.graph_value_label.grid(column=1, row=31, padx=0, pady=5, columnspan=1, rowspan=1)
                self.graph_value_label = ttk.Label(self.frame, text="N.A.", width=15)
                self.graph_value_label.grid(column=3, row=31, padx=0, pady=5, columnspan=1, rowspan=1)

    def expandGraph(self):
        expand_root = tk.Tk()
        expand_root.geometry(f"{design_scheme.windowsize_enlarged_graph[0]}x{design_scheme.windowsize_enlarged_graph[1]}")
        expand_root.title("PU-Spektren Analysator Jumpfinder")
        expand_root.minsize(design_scheme.windowsize_enlarged_graph[0], design_scheme.windowsize_enlarged_graph[1])
        modal = expandedGraph(expand_root, self.type)
        expand_root.wait_window(expand_root)

    def initToolbar(self):
        if self.type == "fit results":
            backend_bases.NavigationToolbar2.toolitems = (
                ('Save', 'Save the figure', 'filesave', 'save_figure'),
            )
        else:
            backend_bases.NavigationToolbar2.toolitems = (
                ('Home', 'Reset original view', 'home', 'home'),
                ('Back', 'Back to  previous view', 'back', 'back'),
                ('Forward', 'Forward to next view', 'forward', 'forward'),

                ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
                ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),

                ('Save', 'Save the figure', 'filesave', 'save_figure'),
            )

    def passing(self):
        pass


class expandedGraph():
    def __init__(self, root, type):
        #super().__init__()

        self.root = root
        self.type = type

        self.style = ttk.Style(self.root)
        self.style.theme_create('enlarged_graphs', parent="alt", settings=design_scheme.getDesignSettings())
        self.style.theme_use("enlarged_graphs")

        self.graph_widget_frame = tk.Frame(self.root, height=120, background=design_scheme.bg_color)
        self.graph_widget_frame.pack(expand=1, fill="both", padx=0, pady=0, side='top')
        self.jump_plot = GraphWidget(self.graph_widget_frame, self.type, True)
        self.button_load_new = ttk.Button(self.graph_widget_frame, width=70, text="Close", command=self.exit)
        self.button_load_new.grid(column=1, row=1000, padx=10, pady=10, ipady=10, columnspan=50, rowspan=50)

    def exit(self):
        self.root.destroy()