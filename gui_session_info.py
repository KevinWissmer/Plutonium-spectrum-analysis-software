import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from open_save import load_file, saveSessionCache, loadSessionCache
from gui_tab_referencespektra import TabReferencespektra
from gui_tab_graph_creator import TabGraphCreator
from gui_tap_baseline_jump_correction import TabCorrections
from gui_tab_fit_options import TabFitOptions
from session_cache import session_cache
import matplotlib
matplotlib.use("Agg")
from gui_plot_widget import GraphWidget
import ntpath
from design import design_scheme
import numpy as np
from datetime import datetime
from gui_jumps import JumpCheck

class sessionInfo():
    def __init__(self, root):
        #super().__init__()

        self.root = root

        self.info_widget_frame = tk.Frame(self.root, height=120, background=design_scheme.bg_color)
        self.info_widget_frame.pack(expand=1, fill="both", padx=0, pady=0, side='top')

        self.style = ttk.Style(self.root)
        self.style.theme_create('enlarged_graphs', parent="alt", settings=design_scheme.getDesignSettings())
        self.style.theme_use("enlarged_graphs")

        self.button_load_new = ttk.Button(self.info_widget_frame, width=70, text="Close", command=self.exit)
        self.button_load_new.grid(column=1, row=1000, padx=10, pady=10, ipady=10, columnspan=50, rowspan=50)

        self.save_list_frame = tk.Frame(self.info_widget_frame, height=60, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)
        self.main_info_frame = tk.Frame(self.info_widget_frame, height=60, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)

        self.cov_frame = tk.Frame(self.info_widget_frame, height=60, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)
        self.cov_frame.grid(column=1, row=20, padx=10, pady=10, ipady=10, columnspan=1, rowspan=10)
        self.cov_frame.propagate(0)

        self.saveListsWidget()
        self.covarWidget()
        self.mainInfoWidget()

    def mainInfoWidget(self):
        self.main_info_frame.grid(column=1, row=10, padx=10, pady=10, ipady=10, columnspan=1, rowspan=10, sticky='wesn')
        self.main_info_frame.propagate(0)

        label_name = ttk.Label(self.main_info_frame, text='general information')
        label_name.grid(row=1, column=10, pady=(10,15))
        label_name = ttk.Label(self.main_info_frame, text='last saved:  '+f"{session_cache.save_date}")
        label_name.grid(row=10, column=10, pady=5, sticky='w')
        label_name = ttk.Label(self.main_info_frame, text='relative file path:  ' + f"{session_cache.filename}")
        label_name.grid(row=20, column=10, pady=5, sticky='w')


    def saveListsWidget(self):

        self.save_list_frame.grid(column=2, row=10, padx=10, pady=10, ipady=10, columnspan=1, rowspan=20)
        self.save_list_frame.propagate(0)

        self.label_name = ttk.Label(self.save_list_frame, text="Save your data to .txt files \n (in saves/saved_data_list)")
        self.label_name.grid(row=10, column=10, padx=10, pady=15, columnspan=11)

        self.generateListSaveButtons()

    def generateListSaveButtons(self):
        i = 0

        for element in session_cache.fit_param_names:
            self.label_name = ttk.Label(self.save_list_frame, text=f"{element}" + " to File", anchor='w')
            self.label_name.config(font=('Helvetica', 8, 'bold'))
            self.label_name.grid(row=40 + i, padx=10, column=10, sticky='we')
            button_edit = ttk.Button(self.save_list_frame, text="save", command=lambda i=i, element=element: self.saveArrayToFile(session_cache.referencespectra_list[i][1], element, session_cache.fitted_params[i][1]))
            button_edit.grid(row=40 + i, column=20, padx=10, pady=5)
            i = i + 1

        self.generateSessionListSaveBtns()

    def generateSessionListSaveBtns(self):
        self.label_name = ttk.Label(self.save_list_frame, text="pure measured data to File", anchor='w')
        self.label_name.config(font=('Helvetica', 8, 'bold'))
        self.label_name.grid(row=60, column=10, padx=10, sticky='we')
        button_edit = ttk.Button(self.save_list_frame, text="save", command=lambda: self.saveArrayToFile(session_cache.original_data_wo_jumps_baseline, "pure_measured_data",1))
        button_edit.grid(row=60, column=20, padx=10, pady=5)

        self.label_name = ttk.Label(self.save_list_frame, text="processed measured data to File", anchor='w')
        self.label_name.config(font=('Helvetica', 8, 'bold'))
        self.label_name.grid(row=61, column=10, padx=10, sticky='we')
        button_edit = ttk.Button(self.save_list_frame, text="save",command=lambda: self.saveArrayToFile(session_cache.data,"processed_measured_data",1))
        button_edit.grid(row=61, column=20, padx=10, pady=5)

        self.label_name = ttk.Label(self.save_list_frame, text="fitted data to File", anchor='w')
        self.label_name.config(font=('Helvetica', 8, 'bold'))
        self.label_name.grid(row=62, column=10, padx=10, sticky='we')
        button_edit = ttk.Button(self.save_list_frame, text="save", command=lambda: self.saveArrayToFile(session_cache.fitted_data, "fitted_data",1))
        button_edit.grid(row=62, column=20, padx=10, pady=5)

        label_name = ttk.Label(self.save_list_frame, text="fitted residuum to File", anchor='w')
        label_name.config(font=('Helvetica', 8, 'bold'))
        label_name.grid(row=63, column=10, padx=10, sticky='we')
        button_edit = ttk.Button(self.save_list_frame, text="save", command=lambda: self.saveArrayToFile(session_cache.fitted_data_residuum, "residuum",1))
        button_edit.grid(row=63, column=20, padx=10, pady=5)


    def saveArrayToFile(self,list,name, factor):
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
        list = self.multiplyListWithFactor(list, factor)
        np.savetxt(f"saves/saved_data_lists/{name}_{dt_string}.txt", np.array(list), fmt="%s")

    def multiplyListWithFactor(self, list, factor):
        result = []
        for element in list:
            result.append([element[0], element[1] * factor])
        return result

    def covarWidget(self):

        if len(session_cache.covar_error_list) > 0:
            self.errorCovarWidget()
            return

        total_rows = len(session_cache.covar_matrix)
        total_columns = len(session_cache.covar_matrix[0])
        self.label_name = ttk.Label(self.cov_frame, text='covariance-\nmatrix', width=15)
        self.label_name.grid(row=0, column=0)
        for i in range(total_rows):
            self.label_vertical = ttk.Label(self.cov_frame, text=f"{session_cache.fit_param_names[i]}\n", width=15)
            self.label_vertical.config(font=('Helvetica', 8, 'bold'))
            self.label_vertical.grid(row=i+1 , column=0)
            self.label_horizontal = ttk.Label(self.cov_frame, text=f"{session_cache.fit_param_names[i]}", width=15)
            self.label_horizontal.config(font=('Helvetica', 8, 'bold'))
            self.label_horizontal.grid(row=0, column=i+1, pady=(50,20), padx=(0,0))

            for j in range(total_columns):
                self.e = ttk.Label(self.cov_frame, text= f"{'{:.3e}'.format(session_cache.covar_matrix[i][j])}\n"  , width=15)
                self.e.config(font=('Helvetica', 8, 'bold'))
                self.e.grid(row=i+1, column=j+1)

    def errorCovarWidget(self):
        self.label_titel = ttk.Label(self.cov_frame, text='covariancematrix could not be estimated')
        self.label_titel.config(font=('Helvetica', 8, 'bold'))
        self.label_titel.grid(row=1, column=0, pady=(10, 10))

        for index, element in enumerate(session_cache.covar_error_list):
            text = f"{index}. {element[0].name}: {element[1]}"
            self.label_error = ttk.Label(self.cov_frame, text=text, width=25)
            self.label_error.config(font=('Helvetica', 8, 'bold'))
            self.label_error.grid(row=index + 2, column=0, pady=(10, 10), padx=(0, 0))

    def exit(self):
        self.root.destroy()
