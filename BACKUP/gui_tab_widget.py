import tkinter as tk
from tkinter import ttk
from session_cache import session_cache, current_reference_spectrum
from gui_plot_widget import GraphWidget
from tkinter import filedialog
from open_save import load_file, save_ref_spectra_list,save_to_ref_spectra_list, load_ref_spectra_list, delete_ref_spectra_list
from tkinter.messagebox import showinfo
import ntpath
from datetime import datetime
import copy
from tkinter.messagebox import askokcancel
from design import design_scheme






class TabReferencespektra(tk.Frame):

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        self.entry_labelname_list = ['Name', 'Type', 'Cuvettesize', 'Norm.-factor', 'Solution']
        self.referencespectra_list_labelnames = ['PUIII', 'PUIV', 'PUV', 'PUVI', 'Verunreinigungen']

        self.current_manipulation_status = 'empty'
        self.manipulation_widget_preset_list = []
        self.spectra_manipulation_frame = tk.Frame(self, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd= 0)
        self.spectra_manipulation_frame.pack(expand=1, fill="both", padx=10, pady=10, side='right')
        self.spectra_manipulation_frame.propagate(0)
        self.initManiPresetList()
        self.spectra_manipulation = self.spectrumManipulationWidget()

        self.graph_frame = tk.Frame(self, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd= 0)
        self.graph_frame.pack(expand=1, fill="both",padx = 10, pady = 10, side= 'right')
        self.graph_frame.propagate(0)
        self.session_plot_referencespectrum = GraphWidget(self.graph_frame, "reference spectrum")

        self.dropdown_frame = tk.Frame(self, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd= 0)
        self.dropdown_frame.pack(expand=1, fill="both", padx=10, pady=10, side= 'left')
        self.dropdown_frame.propagate(0)
        self.referencespectra_list = load_ref_spectra_list()
        self.referencespectra_list_vars = []
        self.var = tk.StringVar(self.dropdown_frame)
        self.var.set('no spectra found')
        self.referencespectra_list_vars_old = [self.var,self.var,self.var,self.var,self.var]

        self.referencespectra_radio_btn_var = tk.IntVar()
        self.dropdown_lists = [[],[],[],[],[]]
        self.createDropdownLists()
        self.create_all_ref_dropdown()

    def initManiPresetList(self):
        self.manipulation_widget_preset_list = []
        for element in self.entry_labelname_list:
            var_1 = tk.StringVar(self.spectra_manipulation_frame)
            var_1.set("empty")
            self.manipulation_widget_preset_list.append(var_1)

    def refreshDropdownListWithSessionCacheData(self):
        self.SaveSessionVarsToRefSpectraListVars()
        self.update_all_dropdowns()

    def UpdateRefSpectraListVarsToSessionSolution(self):
        i = 0
        if session_cache.solution != None:
            for list in self.dropdown_lists:
                for element in list:
                    if session_cache.solution.lower() == self.getRefSpectraSolution(element[1]).lower():
                        self.referencespectra_list_vars[i].set(element)
                i += 1
            self.saveRefSpectraIdsToSessioncache()
            self.update_all_dropdowns()

    def getRefSpectraSolution(self, id):
        for element in self.referencespectra_list:
            if element.id == id:
                return element.solution
        return "N.A."


    def saveRefSpectraIdsToSessioncache(self):
        i = 0
        id_list = []
        for element in self.referencespectra_list_vars:
            try:
                id = int(element.get().replace(')', '').split(',')[1])
                id_list.append([id,self.getRefSpectrumSaveDate(id)])
            except:
                id_list.append([-1,"N.A."])

        session_cache.referencespectra_list_ids = id_list

    def getRefSpectrumSaveDate(self, id):
        date = "N.A."
        for element in self.referencespectra_list:
            if id == element.id:
                date = element.save_date
        return date

    def SaveSessionVarsToRefSpectraListVars(self):
        i = 0
        for element in session_cache.referencespectra_list_ids:
            #print(element)
            self.SaveSingleSessionVarsToRefSpectraListVars(i,element[0],element[1])
            i += 1

    def SaveSingleSessionVarsToRefSpectraListVars(self,i,id,date):
        for element in self.dropdown_lists[i]:
            if id == element[1]:
                if date == self.getRefSpectrumSaveDate(id):
                    self.referencespectra_list_vars[i].set(element)

    def spectrumManipulationWidget(self):
        for widget in self.spectra_manipulation_frame.winfo_children():
            widget.destroy()
        if self.current_manipulation_status == 'empty':
            self.emptySpectrumManipulationWidget()

        if self.current_manipulation_status == 'choosen':
            self.choosenSpectrumManipulationwidget()

        if self.current_manipulation_status == 'edit':
            self.editSpectrumManipulationwidget()

        if self.current_manipulation_status == 'new':
            self.newSpectrumManipulationwidget()

    def emptySpectrumManipulationWidget(self):
        self.label = ttk.Label(self.spectra_manipulation_frame, text="Choose a Spectrum!", width = 17)
        self.label.grid(column=1, row=1, padx=20, pady=20, columnspan=4, rowspan=2)

    def choosenSpectrumManipulationwidget(self):
        i = 0
        for element_name in self.entry_labelname_list:
            self.create_single_spectrumShowWidget(element_name, i)
            i += 1
        #print(self.manipulation_widget_preset_list)
        self.button = ttk.Button(self.spectra_manipulation_frame, text="DELETE SPECTRUM", command=self.deleteSpektrum)
        self.button.grid(column=1, row=i * 2 + 2, padx=20, pady=20, columnspan=4, rowspan=2)

        self.button = ttk.Button(self.spectra_manipulation_frame, text="EDIT SPECTRUM", command=self.openEditorRefSpectrum)
        self.button.grid(column=1, row=i * 2, padx=20, pady=20, columnspan=4, rowspan=2)

    def newSpectrumManipulationwidget(self):
        i = 0
        for element_name in self.entry_labelname_list:
            self.create_single_spectrumManipulationWidget(element_name, i)
            i += 1

        self.button = ttk.Button(self.spectra_manipulation_frame, text="SAVE NEW SPECTRUM",command=self.saveNewSpectrum)
        self.button.grid(column=1, row=i * 2, padx=20, pady=20, columnspan=4, rowspan=2)

    def editSpectrumManipulationwidget(self):
        i = 0
        for element_name in self.entry_labelname_list:
            self.create_single_spectrumManipulationWidget(element_name, i)
            i += 1

        self.button = ttk.Button(self.spectra_manipulation_frame, text="DELETE SPECTRUM", command=self.deleteSpektrum)
        self.button.grid(column=1, row=i * 2 + 2, padx=20, pady=20, columnspan=4, rowspan=2)

        self.button = ttk.Button(self.spectra_manipulation_frame, text="SAVE CHANGES",command=self.SaveEditedSpectrum)
        self.button.grid(column=1, row=i * 2, padx=20, pady=20, columnspan=4, rowspan=2)

    def openEditorRefSpectrum(self):

        self.current_manipulation_status = 'edit'
        self.spectrumManipulationWidget()

    def deleteSpektrum(self):
        answer = askokcancel(title='delete spectrum', message='Are you sure that you want to delete this spectrum?')
        if answer:
            delete_ref_spectra_list(current_reference_spectrum.id)
            current_reference_spectrum.reset()
            self.createDropdownLists()
            self.update_all_dropdowns()
            self.current_manipulation_status = 'empty'
            self.spectrumManipulationWidget()
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            self.session_plot_referencespectrum = GraphWidget(self.graph_frame, "reference spectrum")

    def SaveEditedSpectrum(self):
        #print(float(self.manipulation_widget_preset_list[3].get()))
        if self.ref_spectrum_input_test():
            self.referencespectra_list = load_ref_spectra_list()
            i = 0
            for element in self.referencespectra_list:
                if element.id == current_reference_spectrum.id:

                    #self.referencespectra_list[i].printCurrentRefSpectrum()
                    self.copyToCurrentRefSpectrum(self.referencespectra_list[i])
                    self.updateRefSpectrumInputToCurrent()
                    self.referencespectra_list[i] = copy.deepcopy(current_reference_spectrum)
                    #self.referencespectra_list[i].printCurrentRefSpectrum()
                i += 1

            save_ref_spectra_list(self.referencespectra_list)
            #print(self.referencespectra_list)
            self.createDropdownLists()
            self.update_all_dropdowns()
            self.current_manipulation_status = 'choosen'
            self.updateManipulationPresetList(current_reference_spectrum)
            self.spectrumManipulationWidget()

    def updateRefSpectrumInputToCurrent(self):
        current_reference_spectrum.name = self.manipulation_widget_preset_list[0].get()
        current_reference_spectrum.type = self.manipulation_widget_preset_list[1].get()
        current_reference_spectrum.cuvette_size = self.manipulation_widget_preset_list[2].get()
        current_reference_spectrum.normalization_value = self.manipulation_widget_preset_list[3].get()
        current_reference_spectrum.solution = self.manipulation_widget_preset_list[4].get()
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        current_reference_spectrum.save_date = dt_string

    def create_single_spectrumShowWidget(self,element_name, i):

        ttk.Label(self.spectra_manipulation_frame, text=f"{element_name}:", anchor="e", width = 17).grid(column=1, row=i * 2, padx=5, pady=5, columnspan=2, rowspan=2)
        label = ttk.Label(self.spectra_manipulation_frame, text=f"{self.manipulation_widget_preset_list[i].get()}", width = 17)
        label.grid(column=3, row=i * 2, padx=15, pady=5, columnspan=2, rowspan=2)

    def createDropdownLists(self):
        self.referencespectra_list = load_ref_spectra_list()
        self.dropdown_lists = [[], [], [], [], []]
        for element in self.referencespectra_list:
            if element.type == 'PUIII':
                self.dropdown_lists[0].append([element.createDescriptionName(),element.id])
            if element.type == 'PUIV':
                self.dropdown_lists[1].append([element.createDescriptionName(),element.id])
            if element.type == 'PUV':
                self.dropdown_lists[2].append([element.createDescriptionName(),element.id])
            if element.type == 'PUVI':
                self.dropdown_lists[3].append([element.createDescriptionName(),element.id])
            if element.type == 'Verunreinigungen':
                self.dropdown_lists[4].append([element.createDescriptionName(),element.id])

    def create_single_spectrumManipulationWidget(self,element_name, i):
        ttk.Label(self.spectra_manipulation_frame, text=f"{element_name}", width = 17).grid(column=1, row=i * 2, padx=5, pady=5, columnspan=2, rowspan=2)
        if i == 1:
            opt = ttk.OptionMenu(self.spectra_manipulation_frame, self.manipulation_widget_preset_list[1], self.manipulation_widget_preset_list[1].get(), *self.referencespectra_list_labelnames)
            opt.configure(width= 17)
            opt.grid(column=3, row=i * 2, padx=5, pady=5, columnspan=2, rowspan=2)
        else:
            element = tk.Entry(self.spectra_manipulation_frame, textvariable=self.manipulation_widget_preset_list[i], font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color,width=20)
            element.grid(column=3, row=i*2, padx=5, pady=5, columnspan=2, rowspan=2)

    def update_all_dropdowns(self):
        self.createDropdownLists()
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()
        self.create_all_ref_dropdown()

    def create_all_ref_dropdown(self):
        i = 0
        if len(self.referencespectra_list_vars) > 0:
            self.referencespectra_list_vars_old = self.referencespectra_list_vars
            self.referencespectra_list_vars = []
        for list in self.dropdown_lists:
            self.create_single_ref_dropdown_label(i)
            self.create_single_ref_dropdown(list, i)
            self.create_single_ref_radiobtn(i)
            i += 1
        self.button1 = ttk.Button(self.dropdown_frame, width=25, text="select new Spectrum", command=self.selectNewSpectrum)
        self.button1.grid(column=1, row=12, padx=0, pady=10, ipady=5, columnspan=4, rowspan=2)
        self.button2 = ttk.Button(self.dropdown_frame, width=25, text="update to Solution", command=self.UpdateRefSpectraListVarsToSessionSolution)
        self.button2.grid(column=1, row=14, padx=0, pady=10, ipady=5, columnspan=4, rowspan=2)

    def create_single_ref_dropdown(self,list,i):
        var = tk.StringVar(self.dropdown_frame)
        index = 0
        if len(list) == 0:
            self.referencespectra_list_vars_old[i].set('no spectra found')
        if self.referencespectra_list_vars_old[i].get() != 'no spectra found':
            index = self.get_var_index_ref_dropdown(list, i)
            var.set(list[index])
        else:
            if len(list) > 0:
                var.set(list[index])
            else:
                var.set('no spectra found')
        self.referencespectra_list_vars.append(var)
        opt = ttk.OptionMenu(self.dropdown_frame, var, var.get(), *list)
        opt.config(width= 17)
        opt.grid(column=3, row=i*2, padx=0, pady=10, columnspan=2, rowspan=2)

    def create_single_ref_radiobtn(self,i):
        btn = ttk.Button(self.dropdown_frame, text='show', width=10, command=lambda: self.selection(i))
        btn.grid(column=5, row=i*2, padx=5, pady=5, columnspan=2, rowspan=2)

    def updateManipulationPresetList(self, current_reference_spectrum):
        self.manipulation_widget_preset_list[0].set(current_reference_spectrum.name)
        self.manipulation_widget_preset_list[1].set(current_reference_spectrum.type)
        self.manipulation_widget_preset_list[2].set(current_reference_spectrum.cuvette_size)
        self.manipulation_widget_preset_list[3].set(current_reference_spectrum.normalization_value)
        self.manipulation_widget_preset_list[4].set(current_reference_spectrum.solution)

    def selection(self,i):

        if self.referencespectra_list_vars[i].get() != 'no spectra found':
            self.current_manipulation_status = 'choosen'
            id = int(self.referencespectra_list_vars[i].get().replace(')', '').split(',')[1])
            for element in self.referencespectra_list:
                if element.id == id:
                    self.copyToCurrentRefSpectrum(element)

            self.updateManipulationPresetList(current_reference_spectrum)
            self.spectra_manipulation = self.spectrumManipulationWidget()
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            self.session_plot_referencespectrum = GraphWidget(self.graph_frame, "reference spectrum")

    def copyToCurrentRefSpectrum(self,element):
        current_reference_spectrum.id = element.id
        current_reference_spectrum.type = element.type
        current_reference_spectrum.name = element.name
        current_reference_spectrum.filename = element.filename
        current_reference_spectrum.edges = element.edges
        current_reference_spectrum.cuvette_size = element.cuvette_size
        current_reference_spectrum.normalization_value = element.normalization_value
        current_reference_spectrum.solution = element.solution
        current_reference_spectrum.save_date = element.save_date
        current_reference_spectrum.referencespectra_measurements = element.referencespectra_measurements
        current_reference_spectrum.saved = element.saved

    def get_var_index_ref_dropdown(self,list,i):
        index = 0
        id = int(self.referencespectra_list_vars_old[i].get().replace(')', '').split(',')[1])
        j = 0
        for element in list:
            if element[1] == id:
                index = j
            j += 1
        return index

    def create_single_ref_dropdown_label(self,i):
        w = ttk.Label(self.dropdown_frame, text=self.referencespectra_list_labelnames[i], width = 17)
        w.grid(column=1, row=i*2, columnspan=2, rowspan=2)

    def selectNewSpectrum(self):

        self.current_manipulation_status = 'new'
        self.spectrumManipulationWidget()
        filepath = filedialog.askopenfilename(initialdir="./reference_spectra", title="Select a File")
        load_file(filepath, "ref_spectrum")

        head, tail = ntpath.split(filepath)
        current_reference_spectrum.filename = tail
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.session_plot_referencespectrum = GraphWidget(self.graph_frame, "reference spectrum")

        #print('btn pressed')

    def saveNewSpectrum(self):
        if self.ref_spectrum_input_test():
            current_reference_spectrum.name = self.manipulation_widget_preset_list[0].get()
            current_reference_spectrum.type = self.manipulation_widget_preset_list[1].get()
            current_reference_spectrum.cuvette_size = self.manipulation_widget_preset_list[2].get()
            current_reference_spectrum.normalization_value = self.manipulation_widget_preset_list[3].get()
            current_reference_spectrum.solution = self.manipulation_widget_preset_list[4].get()
            #current_reference_spectrum.printCurrentRefSpectrum()
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            current_reference_spectrum.save_date = dt_string
            #print(self.referencespectra_list)
            #print('saved')
            save_to_ref_spectra_list()
            self.update_all_dropdowns()

    def ref_spectrum_input_test(self):
        input_check_bool = True
        text = 'please check the input of\n'
        if len(str(self.manipulation_widget_preset_list[2].get())) == 0:
            input_check_bool = False
            text = text + '- Cuvettesize not specified\n'
        else:
            try:
                float(self.manipulation_widget_preset_list[2].get())
            except ValueError:
                text = text + '- Cuvettesize is not a number\n'
                input_check_bool = False
        if len(str(self.manipulation_widget_preset_list[3].get())) == 0:
            input_check_bool = False
            text = text + '- Norm.-factor not specified\n'
        else:
            try:
                float(self.manipulation_widget_preset_list[3].get())
            except ValueError:
                text = text + '- Norm.-factor is not a number\n'
                input_check_bool = False
        if len(str(self.manipulation_widget_preset_list[4].get())) == 0:
            input_check_bool = False
            text = text + '- Solution not specified\n'
        if not input_check_bool:
            self.showInfo(text)

        return input_check_bool

    def showInfo(self, text):
        showinfo(
            title='Wrong Input',
            message=text
        )


















class TabGraphCreator(tk.Frame):

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        self.frame = tk.Frame(self, bg=design_scheme.bg_color)
        self.frame.pack(expand=1, fill="both", padx=20, pady=20)
        #self.frame.propagate(0)

        self.lab_1 = ttk.Label(self.frame, text="coming soon!",anchor="center")
        self.lab_1.place(relx=.5, rely=.5, anchor="center")

