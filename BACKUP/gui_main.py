import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from open_save import load_file, saveSessionCache, loadSessionCache
from gui_tab_widget import TabReferencespektra, TabGraphCreator
from gui_tap_baseline_jump_correction import TabCorrections
from gui_tab_fit_options import TabFitOptions
from session_cache import session_cache
import matplotlib
matplotlib.use("Agg")
from gui_plot_widget import GraphWidget
import ntpath
from design import design_scheme
from gui_jumps import JumpCheck

import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(10)

class HeadWidget(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.head_frame = tk.Frame(parent, height=370, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=0, bd= 0)
        self.head_frame.pack(expand=1, fill="x", padx=2)
        self.head_frame.propagate(0)

        self.head_frame3 = tk.Frame(self.head_frame, height=370, width= 170, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd= 0)
        self.head_frame3.pack(expand=1, fill="y", side='right', padx=2, pady=15)
        self.head_frame3.propagate(0)
        self.showResults()


        self.head_frame1 = tk.Frame(self.head_frame, background=design_scheme.bg_color)
        self.head_frame1.pack(expand=1, side='right', padx=2)
        self.head_frame1.propagate(0)
        self.session_plot_fit_spectrum = GraphWidget(self.head_frame1, "fit results")

        self.head_frame2 = tk.Frame(self.head_frame, background=design_scheme.bg_color)
        self.head_frame2.pack(expand=1, side='right')
        self.head_frame2.propagate(0)
        self.session_plot_fit_spectrum2 = GraphWidget(self.head_frame2, "fit")


    def showResults(self):
        for widget in self.head_frame3.winfo_children():
            widget.destroy()
        i=0
        lab_1 = ttk.Label(self.head_frame3, text="fitergebnisse")
        lab_1.grid(column=5, row=2, padx=15, pady=5, columnspan=2, rowspan=2)
        sum = 0.0
        for element in session_cache.fitted_params:
            sum += float(element[1])
        for element in session_cache.fitted_params:
            self.singleResultLine(i,sum)
            i += 1

        label_iterations = ttk.Label(self.head_frame3, text="Total:")
        label_iterations.grid(column=5, row=i * 10 + 4, padx=15, pady=5, columnspan=2, rowspan=2)
        label_result = ttk.Label(self.head_frame3, text=f"{'{:.3e}'.format(sum)}")
        label_result.grid(column=8, row=i * 10 + 4, padx=15, pady=5, columnspan=2, rowspan=2)

        label_iterations = ttk.Label(self.head_frame3, text="Iterations:")
        label_iterations.grid(column=5, row=i * 10 + 6, padx=15, pady=5, columnspan=2, rowspan=2)
        label_result = ttk.Label(self.head_frame3, text=f"{session_cache.run_index}")
        label_result.grid(column=8, row=i * 10 + 6, padx=15, pady=5, columnspan=2, rowspan=2)

    def singleResultLine(self,i,sum):
        value = 0
        if session_cache.fitted_params[i][1] != 0:
            value = round((session_cache.fitted_params[i][1] / sum) * 100, 3)
        label_name = ttk.Label(self.head_frame3, text=f"{session_cache.fit_param_names[i]}")
        label_name.grid(column=5, row=i * 10 + 4, padx=15, pady=5, columnspan=2, rowspan=2)
        label_result = ttk.Label(self.head_frame3, text=f"{'{:.3e}'.format(session_cache.fitted_params[i][1])}  ({value}%)")
        label_result.grid(column=8, row=i * 10 + 4, padx=15, pady=5, columnspan=2, rowspan=2)

class TabWidget(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.tabControl = ttk.Notebook(self.parent)

        self.options_widget_frame = TabFitOptions(self.tabControl)
        self.referencespectra_widget_frame = TabReferencespektra(self.tabControl)
        self.baseline_jumps_correction_widget_frame = TabCorrections(self.tabControl)
        self.graph_creator_widget_frame = TabGraphCreator(self.tabControl)

        self.tabControl.add(self.baseline_jumps_correction_widget_frame, text='Baseline/Jumps')
        self.tabControl.add(self.options_widget_frame, text='Options')
        self.tabControl.add(self.referencespectra_widget_frame, text='Referencespectra')
        #self.tabControl.add(self.baseline_jumps_correction_widget_frame, text='Baseline/Jumps')
        self.tabControl.add(self.graph_creator_widget_frame, text='Graph-creator')

        self.tabControl.pack(expand=1, fill="both", padx=10, pady=10)


    def printTest(self):
        self.referencespectra_widget_frame.update_all_dropdowns()
        for element in self.referencespectra_widget_frame.referencespectra_list_vars:
            print(element.get())



class MainApplication(tk.Frame):
    def __init__(self, parent):


        self.style = ttk.Style()
        self.createStyle()

        tk.Frame.__init__(self, parent)



        self.head_widget = HeadWidget(parent)
        self.showFitResults()
        self.btn_frame = tk.Frame(parent, height = 60, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd= 0)
        self.btn_frame.pack(expand=1, fill="x", padx=10, pady=5, side='top')
        self.btn_frame.propagate(0)
        self.button_load_new = ttk.Button(self.btn_frame, text="load new spectrum",command= self.loadNewSpectrum)
        self.button_load_new.pack(side='left', padx = 20, ipady=5, ipadx=5) #grid(column=8, row=i * 10, padx=20, pady=0, columnspan=1, rowspan=2)
        self.button_load_old = ttk.Button(self.btn_frame, text="load previous session",command=self.loadSession)
        self.button_load_old.pack(side='left', padx = 20, ipady=5, ipadx=5) #grid(column=10, row=i * 10, padx=0, pady=0, columnspan=1, rowspan=2)
        self.button_fit = ttk.Button(self.btn_frame, text="Fit start", command=self.startFit, state= "disabled")
        self.button_fit.pack(side='left',padx=20, ipady=5, ipadx=5)  # grid(column=10, row=i * 10, padx=0, pady=0, columnspan=1, rowspan=2)
        self.button_save = ttk.Button(self.btn_frame, text="save session", command=saveSessionCache, state="disabled")
        self.button_save.pack(side='left', padx=20, ipady=5, ipadx=5)
        self.button_refresh = ttk.Button(self.btn_frame, text="refresh graphs", command=self.showFitResults)
        self.button_refresh.pack(side='left', padx=20, ipady=5, ipadx=5)
        self.tab_widget = TabWidget(parent)

    def createStyle(self):

        self.style.theme_create('PUdesign', parent="alt", settings=design_scheme.getDesignSettings())
        self.style.theme_use("PUdesign")

    def loadSession(self):
        filepath = filedialog.askopenfilename(initialdir="./saves", title="Select a File")
        if len(filepath) != 0:
            loadSessionCache(filepath)
            self.tab_widget.referencespectra_widget_frame.refreshDropdownListWithSessionCacheData()
            self.tab_widget.options_widget_frame.refreshAll()
            self.showFitResults()
            self.button_save["state"] = "normal"
            self.button_fit["state"] = "normal"

    def startFit(self):
        #self.head_widget.plotSessionData()
        self.tab_widget.referencespectra_widget_frame.saveRefSpectraIdsToSessioncache()
        if self.checkAllSavedStatus():
            session_cache.fit()
            self.showFitResults()



    def showFitResults(self):

        #print(session_cache.graphvalue)
        for widget in self.head_widget.head_frame2.winfo_children():
            widget.destroy()
        self.head_widget.session_plot_fit_spectrum2 = GraphWidget(self.head_widget.head_frame2, "fit")#self.head_widget.session_plot_fit_spectrum2.plotData([session_cache.fitted_data, session_cache.data , session_cache.fitted_data_residuum],[], "omitted_area")

        self.head_widget.showResults()

        for widget in self.head_widget.head_frame1.winfo_children():
            widget.destroy()
        self.head_widget.session_plot_fit_spectrum = GraphWidget(self.head_widget.head_frame1, "fit results") #self.head_widget.session_plot_fit_spectrum.plotData([session_cache.fitted_params],[],"bar")


    def checkAllSavedStatus(self):
        #print("sdfsdfsdf:")
        #print(self.tab_widget.options_widget_frame.checkSaveStatus())
        test, text = self.tab_widget.options_widget_frame.checkSaveStatus()
        if test:
            self.tab_widget.options_widget_frame.saveManipulationVarsToSession()
            #session_cache.printAll()
        return test

    def loadNewSpectrum(self):
        filepath = filedialog.askopenfilename(initialdir="./reference_spectra", title="Select a File")
        if not filepath: return
        else:
            session_cache.reset()
        head, tail = ntpath.split(filepath)
        session_cache.filename = tail
        load_file(filepath, "measured_spectrum")
        session_cache.original_data_wo_jumps_baseline = session_cache.original_data
        session_cache.original_data_wo_baseline = session_cache.original_data
        self.tab_widget.baseline_jumps_correction_widget_frame.showCurrentBaselinePlot(False)
        self.button_save["state"] = "normal"
        self.button_fit["state"] = "normal"

        #jump_root = tk.Tk()
        #jump_root.geometry(f"{design_scheme.windowsize_enlarged_graph[0]}x{design_scheme.windowsize_enlarged_graph[1]}")
        #jump_root.title("PU-Spektren Analysator Jumpfinder")
        #jump_root.minsize(design_scheme.windowsize_enlarged_graph[0], design_scheme.windowsize_enlarged_graph[1])
        #modal = JumpCheck(jump_root,"jump")
        #jump_root.wait_window(jump_root)
        self.showFitResults()
        self.tab_widget.options_widget_frame.initSpecsVariables()
        self.tab_widget.options_widget_frame.startSpecsEditing()


def main():
    root = tk.Tk()
    root.geometry(f"{design_scheme.windowsize_main[0]}x{design_scheme.windowsize_main[1]}")
    root.title("PU-Spektren Analysator (early alpha)")
    root.minsize(design_scheme.windowsize_main[0], design_scheme.windowsize_main[1])

    root.configure(background=design_scheme.bg_color)
    MainApplication(root)
    root.mainloop()

if __name__ == '__main__':
    main()

#root = tk.Tk()
#root.title("Tab Widget")
#tab_widget = guiTab.Tabwidget(root)

#root.mainloop()