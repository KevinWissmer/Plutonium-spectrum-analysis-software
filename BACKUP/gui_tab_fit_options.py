import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno, showinfo
from session_cache import session_cache
from design import design_scheme


class TabFitOptions(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        self.specs_list = []
        self.specs_labelname_list = ['Name', 'Cuvettesize', 'Norm.-factor', 'Solution']

        self.current_fit_status = 'none'
        self.specs_manipulation_status = "non_edit"
        self.fit_specs_vars_values_list = []
        self.specs_manipulation_frame = tk.Frame(self, height = 120 , background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd= 0)
        self.specs_manipulation_frame.pack(expand=1, fill="x" , padx=10, pady=10, side='top')
        self.specs_manipulation_frame.propagate(1)
        self.initSpecsVariables()
        #self.specs_manipulation = self.specsManipulationWidget()
        self.specsManipulationWidget()

        self.lower_tab_frame = tk.Frame(self, height=370 , background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd= 0)
        self.lower_tab_frame.pack(expand=1, fill="both", padx=5, pady=5, side='right')
        self.lower_tab_frame.propagate(0)

        self.manipulation_label_names = ["Fit area","omitted area 1","omitted area 2","omitted area 3" ]
        self.manipulation_head_label_names = [ "Minimum", "Maximum", "Consider"]
        self.fit_manipulation_checkbox_consider_vars_list = []
        self.fit_manipulation_vars_values_list = [[], [], [], []]
        self.fit_manipulation_status_list = [["non_edit","non_edit"],["non_edit","non_edit"],["non_edit","non_edit"],["non_edit","non_edit"]]
        self.fit_manipulation_frame = tk.Frame(self.lower_tab_frame, width = 100, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd= 0)
        self.fit_manipulation_frame.pack(expand=1, fill="both", padx=10, pady=10, side='left')
        self.fit_manipulation_frame.propagate(0)
        self.initManipulationVariables()
        #self.fit_manipulation = self.fitManipulationWidget()
        self.fitManipulationWidget()

        self.fit_param_label_names = ["PUIII", "PUIV", "PUV", "PUVI", "Colloid"]
        self.fit_param_type_label_names = ["Start","Minimum","Maximum"]
        self.fit_param_manipulation_status_list = ["non_edit","non_edit","non_edit","non_edit","non_edit"]
        self.fit_param_manipulation_frame = tk.Frame(self.lower_tab_frame, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd= 0)
        self.fit_param_manipulation_frame.pack(expand=1, fill="both", padx=10, pady=10, side='left')
        self.fit_param_manipulation_frame.propagate(0)
        self.fit_param_vars_values_list = []
        self.initParamVariables()
        #self.fit_param_manipulation = self.fitParamManipulationWidget()
        self.fitParamManipulationWidget()

    def refreshAll(self):
        self.refreshSpecs()
        self.refreshFitManipulation()
        self.refreshFitParams()

    def refreshFitParams(self):

        self.fit_param_manipulation_status_list = ["non_edit", "non_edit", "non_edit", "non_edit", "non_edit"]
        i=0
        for element in session_cache.fit_params_values:
            j = 0
            for element2 in element:
                self.fit_param_vars_values_list[i][j].set(element2)
                j += 1
            i += 1
        for widget in self.fit_param_manipulation_frame.winfo_children():
            widget.destroy()
        self.fitParamManipulationWidget()


    def refreshFitManipulation(self):
        self.saveSessionVarsToManipulationVars()
        self.fit_manipulation_status_list = [["non_edit", "non_edit"], ["non_edit", "non_edit"],["non_edit", "non_edit"],["non_edit", "non_edit"]]
        for widget in self.fit_manipulation_frame.winfo_children():
            widget.destroy()
        self.fitManipulationWidget()


    def refreshSpecs(self):
        self.fit_specs_vars_values_list[0].set(session_cache.name)
        self.fit_specs_vars_values_list[1].set(session_cache.cuvette_size)
        self.fit_specs_vars_values_list[2].set(session_cache.normalization_value)
        self.fit_specs_vars_values_list[3].set(session_cache.solution)
        self.updateSpecsManipulationWidget("non_edit")

    def saveSessionVarsToManipulationVars(self):
        for i in range(4):
            if i == 0:
                self.fit_manipulation_vars_values_list[i][0].set(session_cache.fit_start_end[0])
                self.fit_manipulation_vars_values_list[i][1].set(session_cache.fit_start_end[1])
                self.fit_manipulation_checkbox_consider_vars_list[i].set(int(session_cache.fit_start_end[2]))
            else:
                self.fit_manipulation_vars_values_list[i][0].set(session_cache.omitted_areas[i - 1][0])
                self.fit_manipulation_vars_values_list[i][1].set(session_cache.omitted_areas[i - 1][1])
                self.fit_manipulation_checkbox_consider_vars_list[i].set(int(session_cache.omitted_areas[i - 1][2]))
            i += 1

    def saveManipulationVarsToSession(self):
        for i in range(4):
            if i == 0:
                session_cache.fit_start_end[0] = float(self.fit_manipulation_vars_values_list[i][0].get())
                session_cache.fit_start_end[1] = float(self.fit_manipulation_vars_values_list[i][1].get())
                session_cache.fit_start_end[2] = bool(int(self.fit_manipulation_checkbox_consider_vars_list[i].get()))
            else:
                session_cache.omitted_areas[i - 1][0] = float(self.fit_manipulation_vars_values_list[i][0].get())
                session_cache.omitted_areas[i - 1][1] = float(self.fit_manipulation_vars_values_list[i][1].get())
                session_cache.omitted_areas[i - 1][2] = bool(int(self.fit_manipulation_checkbox_consider_vars_list[i].get()))
            i += 1

    def checkSaveStatus(self):
        all_saved = True
        text = 'please save input:\n'
        i = 0
        for element in self.fit_param_manipulation_status_list:
            if element == 'edit':
                all_saved = False
                text = text + f'{self.fit_param_label_names[i]} unsaved\n'
            i += 1
        i = 0
        if self.specs_manipulation_status == "edit":
            all_saved = False
            text = text + 'data specification unsaved\n'

        for element in self.fit_manipulation_status_list:
            if element[0] == 'edit' or element[1] == 'edit':
                all_saved = False
                text = text + f'{self.manipulation_label_names[i]} parameter unsaved\n'
            i += 1

        if not all_saved:
            self.showInfo(text)
        else:
            self.saveManipulationVarsToSession()
        return all_saved, text

    def specsManipulationWidget(self):
        i=0
        for element in self.specs_labelname_list:
            self.createSingleSpecsManipulationElement(i)
            i += 1
        self.createSpecsManiBtn()

    def createSpecsManiBtn(self):
        if self.specs_manipulation_status == "non_edit":
            self.button = ttk.Button(self.specs_manipulation_frame, text="Edit Specs",command=self.startSpecsEditing)
            self.button.grid(column=61, row=5, padx=80, pady=20, columnspan=4, rowspan=2, sticky="E")
        if self.specs_manipulation_status == "edit":
            self.button = ttk.Button(self.specs_manipulation_frame, text="Save Specs",command=self.saveSpectrumSpecs)
            self.button.grid(column=61, row=5, padx=80, pady=20, columnspan=4, rowspan=2, sticky="E")

    def startSpecsEditing(self):
        for element in self.fit_specs_vars_values_list:
        #print(element.get())
            if element.get() == "empty":
                element.set("")
        self.updateSpecsManipulationWidget('edit')

    def saveSpectrumSpecs(self):
        if self.testSpectrumSpecs():
            self.updateSpecsManipulationWidget('non_edit')
            self.saveSpecsToSession()

    def saveSpecsToSession(self):
        session_cache.name = self.fit_specs_vars_values_list[0].get()
        session_cache.cuvette_size = self.fit_specs_vars_values_list[1].get()
        session_cache.normalization_value = self.fit_specs_vars_values_list[2].get()
        session_cache.solution = self.fit_specs_vars_values_list[3].get()

    def testSpectrumSpecs(self):
        text = 'please check the input:\n'
        test_bool = True
        i = 0
        for element in self.specs_labelname_list:
            if len(str(self.fit_specs_vars_values_list[i].get())) == 0:
                test_bool = False
                text = text + f'{element} missing\n'
            elif i == 1 or i == 2:
                try:
                    float(self.fit_specs_vars_values_list[i].get())
                except ValueError:
                    text = text + f'{self.fit_specs_vars_values_list[i].get()} is not a number\n'
                    test_bool = False
            i += 1
        if not test_bool:
            self.showInfo(text)
        return test_bool

    def createSingleSpecsManipulationElement(self,i):
        label = ttk.Label(self.specs_manipulation_frame, text=f"{self.specs_labelname_list[i]}: ")
        label.grid(column=i * 10, row=5, padx=15, pady=5, columnspan=2, rowspan=2)
        if self.specs_manipulation_status == "non_edit":
            label_input = ttk.Label(self.specs_manipulation_frame,text=f"{self.fit_specs_vars_values_list[i].get()}")
            label_input.grid(column=i * 10 + 2, row=5, padx=15, pady=5, columnspan=2, rowspan=2)
        if self.specs_manipulation_status == "edit":
            element = ttk.Entry(self.specs_manipulation_frame, textvariable=self.fit_specs_vars_values_list[i], font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color,width=10)
            element.grid(column=i * 10 + 2, row=5, padx=15, pady=5, columnspan=2, rowspan=2)

    def updateSpecsManipulationWidget(self,status):
        self.specs_manipulation_status = status
        for widget in self.specs_manipulation_frame.winfo_children():
            widget.destroy()
        self.specsManipulationWidget()


    def fitManipulationWidget(self):
        i=0
        self.createFitManipulationHeadLabels()
        for elements in self.manipulation_label_names:
            self.createSingleFitManipulationElement(i,self.manipulation_label_names)
            i += 1

    def createFitManipulationHeadLabels(self):
        label_name = ttk.Label(self.fit_manipulation_frame, text=f"{self.manipulation_head_label_names[0]} :")
        label_name.grid(column=2, row=0, padx=5, pady=5, columnspan=2, rowspan=2, sticky="W")
        label_name = ttk.Label(self.fit_manipulation_frame, text=f"{self.manipulation_head_label_names[1]} :")
        label_name.grid(column=6, row=0, padx=5, pady=5, columnspan=2, rowspan=2, sticky="W")
        label_name = ttk.Label(self.fit_manipulation_frame, text=f"{self.manipulation_head_label_names[2]} :")
        label_name.grid(column=8, row=0, padx=5, pady=5, columnspan=2, rowspan=2, sticky="W")

    def createSingleFitManipulationElement(self,i,label_names):
        self.createSingleFitManipulationElementFirstLine(i,label_names)
        self.createSingleFitManipulationElementSecondLine(i)

    def createSingleFitManipulationElementFirstLine(self,i,label_names):
        label_name = ttk.Label(self.fit_manipulation_frame, text=f"{label_names[i]} :")
        label_name.grid(column=1, row=i * 10+2, padx=5, pady=5, columnspan=1, rowspan=2, sticky="E")
        self.createSingleFitManipulationElementFirstLineInput(i,0,2)
        label_middle = ttk.Label(self.fit_manipulation_frame, text=f"-")
        label_middle.grid(column=4, row=i * 10+2, padx=5, pady=5, columnspan=2, rowspan=2)
        self.createSingleFitManipulationElementFirstLineInput(i, 1, 6)


    def createSingleFitManipulationElementFirstLineInput(self,i1,i2,col):
        if self.fit_manipulation_status_list[i1][i2] == "non_edit":
            label_name = ttk.Label(self.fit_manipulation_frame, text=f"{self.fit_manipulation_vars_values_list[i1][i2].get()}")
            label_name.grid(column=col, row=i1 * 10+2, padx=5, pady=5, columnspan=2, rowspan=2)
        if self.fit_manipulation_status_list[i1][i2] == "edit":
            element = tk.Entry(self.fit_manipulation_frame, font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color, width=10, textvariable=self.fit_manipulation_vars_values_list[i1][i2])
            element.grid(column=col, row=i1 * 10+2, padx=5, pady=5, columnspan=2, rowspan=2)

    def createSingleFitManipulationElementSecondLine(self, i):

        self.createSingleFitManipulationElementSecondLineBtn(i,0,2)
        self.createSingleFitManipulationElementSecondLineBtn(i,1, 6)

        checkbox_1 = ttk.Checkbutton(self.fit_manipulation_frame, text="", variable=self.fit_manipulation_checkbox_consider_vars_list[i], command=self.saveConsiderationToSession)
        checkbox_1.grid(column=8, row=i * 10+2, padx=5, pady=5, columnspan=2, rowspan=2)

    def createSingleFitManipulationElementSecondLineBtn(self, i,i2,col):
        if self.fit_manipulation_status_list[i][i2] == "non_edit":
            button_edit = ttk.Button(self.fit_manipulation_frame, text="edit", command=lambda: self.updateFitManipulation('edit',i,i2))
            button_edit.grid(column=col, row=i * 10 + 2+2, padx=0, pady=0, columnspan=1, rowspan=2)
        if self.fit_manipulation_status_list[i][i2] == "edit":
            button_save = ttk.Button(self.fit_manipulation_frame, text="save", command=lambda: self.updateFitManipulation('non_edit',i,i2))
            button_save.grid(column=col, row=i * 10 + 2+2, padx=0, pady=0, columnspan=1, rowspan=2)
        button_get_1 = ttk.Button(self.fit_manipulation_frame, text="get value", command=lambda: self.updateFitManipulationGetValue(i,i2))
        button_get_1.grid(column=col +1, row=i * 10 + 2+2, padx=10, pady=0, columnspan=1, rowspan=2)

    def updateFitManipulation(self,status,i1,i2):
        test = True
        if status == 'non_edit':
            test = self.fitManipulationInputTest(i1,i2)
        elif self.fit_manipulation_vars_values_list[i1][i2].get() == "empty":
            self.fit_manipulation_vars_values_list[i1][i2].set("")
        if test:
            self.fit_manipulation_status_list[i1][i2] = status
            self.saveManipulationVarsToSession()
            for widget in self.fit_manipulation_frame.winfo_children():
                widget.destroy()
            self.fitManipulationWidget()

    def updateFitManipulationGetValue(self, i1, i2):
        if session_cache.graphvalue != "N.A." and self.fitManipulationMinMaxTest(session_cache.graphvalue, i1, i2):
            self.fit_manipulation_status_list[i1][i2] = 'non_edit'
            self.fit_manipulation_vars_values_list[i1][i2].set(session_cache.graphvalue)
            self.saveManipulationVarsToSession()
            for widget in self.fit_manipulation_frame.winfo_children():
                widget.destroy()
            self.fitManipulationWidget()

    def fitManipulationMinMaxTest(self, limit, i1, i2):
        input_check_bool, text, minimum, maximum = self.getFitManipulationMinMax(limit, i1, i2)
        if minimum > maximum:
            text += "Minimum should not be higher then maximum\n"
            input_check_bool = False
        if not input_check_bool:
            self.showInfo(text)
        return input_check_bool

    def getFitManipulationMinMax(self, limit, i1, i2):
        text = ""
        input_check_bool = True
        minimum = 0
        maximum = 100000
        if i2 == 0:
            if self.fit_manipulation_status_list[i1][1] == "non_edit":
                minimum = limit
                maximum = float(self.fit_manipulation_vars_values_list[i1][1].get())
        if i2 == 1:
            if self.fit_manipulation_status_list[i1][0] == "non_edit":
                maximum = limit
                minimum = float(self.fit_manipulation_vars_values_list[i1][0].get())
        return input_check_bool, text, minimum, maximum


    def fitManipulationInputTest(self,i1,i2):
        input_check_bool = True
        text = 'please check the input:\n'
        if len(str(self.fit_manipulation_vars_values_list[i1][i2].get())) == 0:
            self.fit_manipulation_vars_values_list[i1][i2].set("empty")
        else:
            try:
                float(self.fit_manipulation_vars_values_list[i1][i2].get())
            except ValueError:
                text = text + f'{self.fit_manipulation_vars_values_list[i1][i2].get()} is not a number\n'
                input_check_bool = False

        if not input_check_bool:
            self.showInfo(text)
        else:
            input_check_bool = self.fitManipulationMinMaxTest(float(self.fit_manipulation_vars_values_list[i1][i2].get()), i1, i2)
        return input_check_bool

    def fitParamManipulationWidget(self):
        i = 0
        for elements in self.fit_param_label_names:
            self.createSingleFitParamManipulationElement(i, self.fit_param_label_names)
            i += 1
        #var_coll = tk.IntVar()
        #checkbox_1 = tk.Checkbutton(self.fit_param_manipulation_frame, bg="grey", text="consider colloides", variable=var_coll)
        #checkbox_1.grid(column=3, row=70 , padx=15, pady=5, columnspan=2, rowspan=2, sticky="W")

    def createSingleFitParamManipulationElement(self,i,label_names):
        self.createSingleFitParamManipulationElementLabels(i,label_names)
        self.createFitParamManipulationHeadLabels()
        if self.fit_param_manipulation_status_list[i] == 'non_edit':
            self.createSingleFitParamManipulationElementDisplay(i)
        if self.fit_param_manipulation_status_list[i] == 'edit':
            self.createSingleFitParamManipulationElementInput(i)

    def createFitParamManipulationHeadLabels(self):
        i = 0
        for element in self.fit_param_type_label_names:
            label_name = ttk.Label(self.fit_param_manipulation_frame, text=f"{element} :")
            label_name.grid(column=4 + (2 * i), row= 1, padx=25, pady=15, columnspan=1, rowspan=1, sticky="W")
            i += 1
        label_name = ttk.Label(self.fit_param_manipulation_frame, text=f"vary value:")
        label_name.grid(column=12, row=1, padx=25, pady=15, columnspan=1, rowspan=1, sticky="W")


    def createSingleFitParamManipulationElementDisplay(self,i):
        label = ttk.Label(self.fit_param_manipulation_frame, text=self.fit_param_vars_values_list[i][0].get())
        label.grid(column=4, row=i * 10 + 2, padx=5, pady=5, columnspan=2, rowspan=2)
        label = ttk.Label(self.fit_param_manipulation_frame, text=self.fit_param_vars_values_list[i][1].get())
        label.grid(column=6, row=i * 10 + 2, padx=5, pady=5, columnspan=2, rowspan=2)
        label = ttk.Label(self.fit_param_manipulation_frame, text=self.fit_param_vars_values_list[i][2].get())
        label.grid(column=8, row=i * 10 + 2, padx=5, pady=5, columnspan=2, rowspan=2)
        button_edit = ttk.Button(self.fit_param_manipulation_frame, text="edit", command=lambda: self.updateFitParamManipulation('edit',i))
        button_edit.grid(column=10, row=i * 10 + 2, padx=20, pady=0, columnspan=1, rowspan=2)
        checkbox_vary = ttk.Checkbutton(self.fit_param_manipulation_frame, text="",variable=self.fit_param_vars_values_list[i][3],command=self.saveAllFitParamVaryValues)
        checkbox_vary.grid(column=12, row=i * 10 + 2, padx=5, pady=5, columnspan=2, rowspan=2)#, sticky="W")


    def createSingleFitParamManipulationElementInput(self,i):
        element = tk.Entry(self.fit_param_manipulation_frame, font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color, textvariable=self.fit_param_vars_values_list[i][0],width=10)
        element.grid(column=4, row=i * 10 + 2, padx=5, pady=5, columnspan=2, rowspan=2)
        element = tk.Entry(self.fit_param_manipulation_frame, font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color, textvariable=self.fit_param_vars_values_list[i][1],width=10)
        element.grid(column=6, row=i * 10 + 2, padx=5, pady=5, columnspan=2, rowspan=2)
        element = tk.Entry(self.fit_param_manipulation_frame, font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color, textvariable=self.fit_param_vars_values_list[i][2],width=10)
        element.grid(column=8, row=i * 10 + 2, padx=5, pady=5, columnspan=2, rowspan=2)
        button_edit = ttk.Button(self.fit_param_manipulation_frame, text="save",command=lambda: self.saveFitParam(i))
        button_edit.grid(column=10, row=i * 10 + 2, padx=20, pady=0, columnspan=1, rowspan=2)
        checkbox_vary = ttk.Checkbutton(self.fit_param_manipulation_frame, text="", variable=self.fit_param_vars_values_list[i][3],command= self.saveAllFitParamVaryValues)
        checkbox_vary.grid(column=12, row=i * 10 + 2, padx=5, pady=5, columnspan=2, rowspan=2, sticky="W")

    def createSingleFitParamManipulationElementLabels(self,i,label_names):
        label_name = ttk.Label(self.fit_param_manipulation_frame, text=f"{label_names[i]} :")
        label_name.grid(column=1, row=i * 10  + 2, padx=25, pady=10, columnspan=1, rowspan=2)#, sticky="E")

    def saveAllFitParamVaryValues(self):
        j = 0
        for element in self.fit_param_vars_values_list:
            session_cache.fit_params_values[j][3] = element[3].get()
            j += 1

    def saveFitParam(self,i):
        j = 0
        if self.checkFitParam(i):
            for element in self.fit_param_vars_values_list[i]:
                if len(str(element.get())) == 0:
                    element.set("empty")
                session_cache.fit_params_values[i][j] = element.get()
                j += 1
            self.updateFitParamManipulation('non_edit', i)
    #print(session_cache.fit_params_values[i])


    def checkFitParam(self,i):
        input_check_bool = True
        text = 'please check the input:\n'
        j = 0
        for element in self.fit_param_vars_values_list[i]:
            if len(str(element.get())) != 0 and j != 3:
                try:
                    float(element.get())
                except ValueError:
                    text = text + f'{element.get()} is not a number\n'
                    input_check_bool = False
            j += 1
        if input_check_bool and len(str(self.fit_param_vars_values_list[i][1].get())) != 0 and len(str(self.fit_param_vars_values_list[i][2].get())) != 0:
            #print("dasdasd")
            if float(self.fit_param_vars_values_list[i][1].get()) > float(self.fit_param_vars_values_list[i][2].get()):
                text = text + f'maximum is lower then minimum\n'
                input_check_bool = False
        if not input_check_bool:
            self.showInfo(text)
        return input_check_bool


    def updateFitParamManipulation(self, status, i):
        self.fit_param_manipulation_status_list[i] = status
        for element in self.fit_param_vars_values_list[i]:
            if element.get() == "empty" and status == "edit":
                element.set("")
            if len(str(element.get())) == 0 and status == "non_edit":
                element.set("empty")
        for widget in self.fit_param_manipulation_frame.winfo_children():
            widget.destroy()
        self.fitParamManipulationWidget()

    def confirm(self):
        answer = askyesno(title='delete spectrum', message='Are you sure that you want to delete this spectrum?')
        #if answer:
        #    print('blabla')

    def initParamVariables(self):
        self.fit_param_vars_values_list = [[], [], [], [], []]
        i = 0
        for element in self.fit_param_vars_values_list:
            var_start = tk.StringVar(self.fit_param_manipulation_frame)
            var_start.set(0.5)
            var_min = tk.StringVar(self.fit_param_manipulation_frame)
            var_min.set(-0.05)
            var_max = tk.StringVar(self.fit_param_manipulation_frame)
            var_max.set("empty")
            var_max = tk.StringVar(self.fit_param_manipulation_frame)
            var_max.set("empty")
            var_vary = tk.StringVar(self.fit_param_manipulation_frame)
            var_vary.set(True)
            self.fit_param_vars_values_list[i] = [var_start, var_min, var_max, var_vary]
            i += 1

    def initManipulationVariables(self):
        self.fit_manipulation_vars_values_list = [["empty","empty"], ["empty","empty"], ["empty","empty"], ["empty","empty"]]
        i = 0
        min = 430
        max = 850
        self.fit_manipulation_checkbox_consider_vars_list = []
        for element in self.fit_manipulation_vars_values_list:
            var_1 = tk.StringVar(self.fit_manipulation_frame)
            var_1.set(min)
            var_2 = tk.StringVar(self.fit_manipulation_frame)
            var_2.set(max)
            var_3 = tk.StringVar(self.fit_manipulation_frame)
            var_3.set(False)
            self.fit_manipulation_vars_values_list[i] = [var_1, var_2]
            self.fit_manipulation_checkbox_consider_vars_list.append(var_3)
            i += 1
            max=0
            min=0


    def initSpecsVariables(self):
        self.fit_specs_vars_values_list = []
        for element in self.specs_labelname_list:
            var_1 = tk.StringVar(self.specs_manipulation_frame)
            var_1.set("empty")
            self.fit_specs_vars_values_list.append(var_1)

    def showInfo(self, text):
        showinfo(
            title='Wrong Input',
            message=text
        )

    def saveConsiderationToSession(self):
        session_cache.fit_start_end[2] = bool(int(self.fit_manipulation_checkbox_consider_vars_list[0].get()))
        session_cache.omitted_areas[0][2] = bool(int(self.fit_manipulation_checkbox_consider_vars_list[1].get()))
        session_cache.omitted_areas[1][2] = bool(int(self.fit_manipulation_checkbox_consider_vars_list[2].get()))
        session_cache.omitted_areas[2][2] = bool(int(self.fit_manipulation_checkbox_consider_vars_list[3].get()))
        self.saveManipulationVarsToSession()

    def printhello(self):
        print(f"{self.fit_manipulation_checkbox_consider_vars_list[0].get()},{self.fit_manipulation_checkbox_consider_vars_list[1].get()},{self.fit_manipulation_checkbox_consider_vars_list[2].get()},{self.fit_manipulation_checkbox_consider_vars_list[3].get()}")

    def passing(self):
        for element in self.fit_param_vars_values_list:
            print(element[3].get())