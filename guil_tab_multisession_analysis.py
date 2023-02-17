import tkinter as tk
from tkinter import ttk
from session_cache import session_cache, current_reference_spectrum, current_analysis
from gui_plot_widget import GraphWidget
from open_save import load_file, saveCurrentAnalysis, loadCurrentAnalysis, getSessionFromFile
import textwrap
from tkinter import filedialog
from open_save import load_file, save_ref_spectra_list,save_to_ref_spectra_list, load_ref_spectra_list, delete_ref_spectra_list
from tkinter.messagebox import showinfo
import ntpath
from datetime import datetime
import copy
from tkinter.messagebox import askokcancel
from design import design_scheme


#Pu(III)%-&PuColl

class TabMultisessionAnalysis(tk.Frame):

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        self.main_frame = tk.Frame(self, bg=design_scheme.bg_color)
        self.main_frame.pack(expand=1, fill="both", padx=20, pady=20)
        #self.frame.propagate(0)

        self.data_collection_frame = tk.Frame(self.main_frame, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)
        self.data_collection_frame.pack(expand=1, fill="both", padx=10, pady=10, side='left')
        self.data_collection_frame.propagate(0)

        self.graph_manipulation_frame = tk.Frame(self.main_frame, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)
        self.graph_manipulation_frame.pack(expand=1, fill="both", padx=10, pady=10, side='right')
        self.graph_manipulation_frame.propagate(0)

        self.graph_frame = tk.Frame(self.main_frame, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)
        self.graph_frame.pack(expand=1, fill="both", padx=10, pady=10, side='right')
        self.graph_frame.propagate(0)
        self.graph_plot_widget = GraphWidget(self.graph_frame, "multi Analysis fits")
        self.graph_labels = ['Fit', 'Pu(III)', 'Pu(IV)', 'Pu(V)', 'Pu(VI)', 'PuColl', 'Polynom', 'Data']
        self.btn_list_graphs = []

        self.name_manipulation_status = ["non_edit", "non_edit", "non_edit", "non_edit", "non_edit", "non_edit", "non_edit", "non_edit"]
        self.name_manipulation_var_list = []
        self.max_count_graphs = 8

        self.initNameVariables()
        self.initDataCollectioFrame()
        self.initGraphManipulationFrame()
        self.createGraphBtn()


    def initNameVariables(self):
        self.name_manipulation_var_list = []
        for element in self.name_manipulation_status:
            var_name = tk.StringVar(self.data_collection_frame)
            var_name.set("empty")
            self.name_manipulation_var_list.append(var_name)

    def initDataCollectioFrame(self):
        for widget in self.data_collection_frame.winfo_children():
            widget.destroy()

        label = ttk.Label(self.data_collection_frame, text=f"Graphs:", width=10)
        label.grid(column=10, row=20, padx=10, pady=10, columnspan=7, rowspan=2)

        self.updateSingleDataList()
        self.updateGraph()

    def updateSingleDataList(self):
        i=0
        for element in current_analysis.data_list:
            self.name_manipulation_var_list[i].set(element.name)
            self.createSingleDataLine(i)
            i += 1

    def createGraphBtn(self):
        i = 0
        j = 0
        k = 0
        span = 10
        for element in self.graph_labels:
            if (i == 3 or i == 6):
                i = 0
                j = j + 1
            if k == 8:
                span = 5
            if k == 9:
                self.btn_list_graphs.append(ttk.Button(self.graph_manipulation_frame, width=span, text=element, command=lambda k=k: self.changeCurrentDataKey(self.graph_labels[k])))
                self.btn_list_graphs[k].grid(column=25, row=20 + j - 1, padx=(5, 0), pady=(10, 0), columnspan=1, rowspan=1)
            else:
                self.btn_list_graphs.append(ttk.Button(self.graph_manipulation_frame, width=span, text=element,command=lambda k=k: self.changeCurrentDataKey(self.graph_labels[k])))
                self.btn_list_graphs[k].grid(column=i * 10, row=20 + j, padx=(20, 0), pady=(10, 0), columnspan=span, rowspan=1)

            i += 1
            k += 1

    def changeCurrentDataKey(self, key):
        current_analysis.current_data_key = key
        self.updateGraph()

    def loadSingleData(self):
        if 'editing' in self.name_manipulation_status:
            self.showAlert("please save current editing!")
        else:
            if len(current_analysis.data_list) < self.max_count_graphs:
                filepath = filedialog.askopenfilename(initialdir="./saves", title="Select a File")
                if len(filepath) != 0:
                    single_data = getSessionFromFile(filepath)
                    if single_data != "err:loading":
                        if single_data != "err:notfitted":
                            current_analysis.addSingleData(single_data)
                            self.initDataCollectioFrame()
                        else:
                            self.showAlert("please choose fitted data!")
                    else:
                        self.showAlert("please choose correct session cache file")
            else:
                self.showAlert(f"reached maximum count of graphs (currently {self.max_count_graphs})")

    def loadAnalysis(self):
        filepath = filedialog.askopenfilename(initialdir="./saves/multy_session_analysis", title="Select a File")
        if len(filepath) != 0:
            loadCurrentAnalysis(filepath)
            self.initNameVariables()
            self.initDataCollectioFrame()

    def saveAnalysis(self):
        if len(current_analysis.data_list) > 0:
            saveCurrentAnalysis()
        else:
            self.showAlert("please add minimum 1 session")


    def createSingleDataLine(self, num):
        self.generateInputElement(num)
        self.generateInputBtnElement(num)
        self.generateBtnUpDown(num)
        self.generateBtnDelete(num)

    def generateInputElement(self, num):
        if self.name_manipulation_status[num] == "non_edit":
            label = ttk.Label(self.data_collection_frame, text=f"{current_analysis.data_list[num].name}", width=10)
            label.grid(column=10, row=10 * num + 30, padx=10, pady=10, columnspan=14, rowspan=2)
        else:
            element = ttk.Entry(self.data_collection_frame, textvariable=self.name_manipulation_var_list[num], font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color,width=10)
            element.grid(column=10, row=10 * num + 30, padx=10, pady=10, columnspan=14, rowspan=2)

    def generateInputBtnElement(self, num):
        if self.name_manipulation_status[num] == "non_edit":
            button_edit_name = ttk.Button(self.data_collection_frame, width=6, text='edit', command=lambda num=num: self.editSingleDataName(num))
            button_edit_name.grid(column=25, row=10 * num + 30, padx=(10, 0), pady=3, columnspan=1, rowspan=1)
        else:
            button_edit_name = ttk.Button(self.data_collection_frame, width=6, text='save', command=lambda num=num: self.saveSingleDataName(num))
            button_edit_name.grid(column=25, row=10 * num + 30, padx=(10, 0), pady=3, columnspan=1, rowspan=1)

    def generateBtnUpDown(self, num):
        button_down = ttk.Button(self.data_collection_frame, width=2, text='\u2193', command=lambda num=num: self.lowerSingleData(num))
        button_down.grid(column=30, row=10 * num + 30, padx=(10, 0), pady=1, columnspan=1, rowspan=1)
        button_up = ttk.Button(self.data_collection_frame, width=2, text='\u2191', command=lambda num=num: self.liftSingleData(num))
        button_up.grid(column=31, row=10 * num + 30, padx=(0, 0), pady=1, columnspan=1, rowspan=1)

    def generateBtnDelete(self, num):
        button_delete = ttk.Button(self.data_collection_frame, width=2, text='\U0001F5D1', command=lambda num=num: self.deleteSingleData(num))
        button_delete.grid(column=33, row=10 * num + 30, padx=(10, 0), pady=3, columnspan=1, rowspan=1)

    def editSingleDataName(self, num):
        self.name_manipulation_status[num] = 'editing'
        self.initDataCollectioFrame()

    def saveSingleDataName(self, num):
        name_value = self.name_manipulation_var_list[num].get()
        if len(name_value) > 10:
            self.showAlert("maximum of 10 characters exceeded!")
        else:
            self.name_manipulation_status[num] = 'non_edit'
            current_analysis.data_list[num].name = name_value
            self.initDataCollectioFrame()

    def liftSingleData(self, num):
        if num > 0:
            tmp = current_analysis.data_list[num]
            current_analysis.data_list[num] = current_analysis.data_list[num - 1]
            current_analysis.data_list[num - 1] = tmp
        self.initDataCollectioFrame()

    def lowerSingleData(self, num):
        if num < len(current_analysis.data_list) - 1:
            tmp = current_analysis.data_list[num]
            current_analysis.data_list[num] = current_analysis.data_list[num + 1]
            current_analysis.data_list[num + 1] = tmp
        self.initDataCollectioFrame()

    def deleteSingleData(self, num):
        current_analysis.data_list.pop(num)
        self.initDataCollectioFrame()

    def initGraphManipulationFrame(self):
        button_load = ttk.Button(self.graph_manipulation_frame, width=12, text='load session', command=self.loadSingleData)
        button_load.grid(column=0, row=10, padx=(20, 0), pady=3, columnspan=1, rowspan=1)
        button_save = ttk.Button(self.graph_manipulation_frame, width=12, text='load Analysis', command=self.loadAnalysis )
        button_save.grid(column=10, row=10, padx=(20, 0), pady=3, columnspan=1, rowspan=1)
        button_loadAll = ttk.Button(self.graph_manipulation_frame, width=12, text='save Analysis', command=self.saveAnalysis )
        button_loadAll.grid(column=20, row=10, padx=(20, 0), pady=3, columnspan=1, rowspan=1)

    def updateGraph(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_plot_widget = GraphWidget(self.graph_frame, "multi Analysis fits")


    def showAlert(self, text):
        showinfo(
            title='Warning',
            message=text
        )