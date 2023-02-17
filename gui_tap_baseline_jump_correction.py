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


import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.interpolate import CubicSpline



class TabCorrections(tk.Frame):

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        self.als_manipulation_status = ["non_edit","non_edit"]
        self.offset_manipulation_status = ["non_edit", "non_edit"]
        self.offset_manipulation_values = [[0,0],["empty","empty"]]
        self.als_manipulation_values = [0.0000001,10000]
        self.jump_manipulation_values = "N.A."
        self.current_jump = [0,0,[0]]

        self.baseline_frame = tk.Frame(self,width=560, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd= 0)
        self.baseline_frame.pack(expand=1, fill="y", padx=10, pady=10, side='left')
        self.baseline_frame.propagate(0)
        self.initOffsetManiVars()
        self.initALSManiVars()
        self.baselineWidget()

        self.graph_wrapper_frame = tk.Frame(self,width=580 , background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)
        self.graph_wrapper_frame.pack(expand=1, fill="y", padx=0, pady=10, side='left')
        self.graph_wrapper_frame.propagate(0)

        self.graph_frame = tk.Frame(self.graph_wrapper_frame,  background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=0, bd= 0)
        self.graph_frame.grid(column=1, row=1, padx=0, pady=0, columnspan=3, rowspan=2)#.pack(expand=1, fill="y",padx = 0, pady = 0, side= 'left')
        self.graph_frame.propagate(0)

        self.showCurrentBaselinePlot(False)

        self.jump_frame = tk.Frame(self,width=440 , background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd= 0)
        self.jump_frame.pack(expand=1, fill="y", padx=10, pady=10, side= 'left')
        self.jump_frame.propagate(0)
        self.initJumpVars()
        self.createJumpWidget()

    def createJumpWidget(self):
        label = ttk.Label(self.jump_frame, text="Data-Jumps")
        label.grid(column=1, row=1, padx=10, pady=15, columnspan=3, rowspan=2)

        label = ttk.Label(self.jump_frame, text=f"{self.jump_manipulation_values.get()} nm")
        label.grid(column=1, row=3, padx=10, pady=15, columnspan=3, rowspan=2)

        button_calc = ttk.Button(self.jump_frame, text="calculate", command= self.calculateJump)
        button_calc.grid(column=1, row=5, padx=5, pady=0, columnspan=1, rowspan=2)

        button_get = ttk.Button(self.jump_frame, text="get value", command= self.jumpGetValue)
        button_get.grid(column=3, row=5, padx=5, pady=0, columnspan=1, rowspan=2)

        label = ttk.Label(self.jump_frame, text="confirmed Data-Jumps:")
        label.grid(column=1, row=10, padx=10, pady=20, columnspan=3, rowspan=2)
        i=2
        for element in session_cache.datajumps:
            self.label = ttk.Label(self.jump_frame, text=f"x = {element[0]} adjustment = {element[1]}")
            self.label.grid(column=1, row=10 * i, padx=10, pady=10, columnspan=3, rowspan=2)
            i += 1

    def jumpGetValue(self):
        if session_cache.graphvalue_baseline != "N.A.":
            value = round(float(session_cache.graphvalue_baseline[0]),2)
            self.jump_manipulation_values.set(value)
            self.updateJumpWidget()

    def calculateJump(self):
        if self.jump_manipulation_values.get() != "N.A.":
            jump_value = float(self.jump_manipulation_values.get())
            session_cache.original_data_wo_baseline = self.sortAndUniq(session_cache.original_data_wo_baseline)
            i=0
            new_list = []
            distance = 0
            for element in session_cache.original_data_wo_baseline:

                if i > 0:
                    if session_cache.original_data_wo_baseline[i - 1][0] < jump_value and session_cache.original_data_wo_baseline[i][0] > jump_value:
                        distance = session_cache.original_data_wo_baseline[i][1] - session_cache.original_data_wo_baseline[i - 1][1]
                        self.current_jump = [session_cache.original_data_wo_baseline[i - 1][0], distance,[0]]

                new_list.append([element[0],element[1] - distance])
                i += 1
            self.current_jump[2] = new_list
            session_cache.current_jump = self.current_jump
            self.showCurrentJump(True)

    def showCurrentJump(self, btn_bool):
        for widget in self.graph_wrapper_frame.winfo_children():
            widget.destroy()
        self.graph_frame = tk.Frame(self.graph_wrapper_frame, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=0, bd=0)
        self.graph_frame.grid(column=1, row=1, padx=0, pady=0, columnspan=3, rowspan=2)
        self.graph_frame.propagate(0)
        GraphWidget(self.graph_frame, "jump")
        if btn_bool:
            self.createConfirmDeclineBtnJump()

    def createConfirmDeclineBtnJump(self):
        button_yes = ttk.Button(self.graph_wrapper_frame, text="Confirm", width=20, command=self.confirmJump)
        button_yes.grid(column=1, row=4, padx=20, pady=0, ipadx=5, ipady=5, columnspan=1, rowspan=2)

        button_no = ttk.Button(self.graph_wrapper_frame, text="Decline", width=20, command=self.declineJump)
        button_no.grid(column=3, row=4, padx=20, pady=0, ipadx=5, ipady=5, columnspan=1, rowspan=2)

    def confirmJump(self):
        session_cache.datajumps.append([self.current_jump[0], self.current_jump[1]])
        session_cache.original_data_wo_baseline = self.current_jump[2]
        session_cache.original_data = self.current_jump[2]
        self.showCurrentBaselinePlot(False)
        self.updateJumpWidget()

    def declineJump(self):
        self.showCurrentBaselinePlot(False)
        session_cache.current_jump = [0,0,[[400,0],[850,0]]]

    def updateJumpWidget(self):
        for widget in self.jump_frame.winfo_children():
            widget.destroy()
        self.createJumpWidget()


    def showCurrentBaselinePlot(self, btn_bool):
        for widget in self.graph_wrapper_frame.winfo_children():
            widget.destroy()
        self.graph_frame = tk.Frame(self.graph_wrapper_frame, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=0, bd=0)
        self.graph_frame.grid(column=1, row=1, padx=0, pady=0, columnspan=3, rowspan=2)  # .pack(expand=1, fill="y",padx = 0, pady = 0, side= 'left')
        self.graph_frame.propagate(0)
        GraphWidget(self.graph_frame, "baseline")
        if btn_bool:
            self.createConfirmDeclineBtnBaseline()

    def baselineWidget(self):
        for widget in self.baseline_frame.winfo_children():
            widget.destroy()
        self.createOffsetWidget()
        self.createAsymmetricLeastSquaresBaselineWidget()
        #self.createCurrentBaselineWidget()

    def createConfirmDeclineBtnBaseline(self):
        button_yes = ttk.Button(self.graph_wrapper_frame, text="Confirm", width=20, command=self.confirm)
        button_yes.grid(column=1, row=4, padx=20, pady=0, ipadx=5, ipady=5, columnspan=1, rowspan=2)

        button_no = ttk.Button(self.graph_wrapper_frame, text="Decline", width=20, command=self.decline)
        button_no.grid(column=3, row=4, padx=20, pady=0, ipadx=5, ipady=5, columnspan=1, rowspan=2)

    def createOffsetWidget(self):

        self.offset_frame = tk.Frame(self.baseline_frame, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)
        self.offset_frame.pack(expand=1, fill="both", padx=10, pady=10, side='top')
        self.offset_frame.propagate(0)

        self.label = ttk.Label(self.offset_frame, text="Offset")
        self.label.grid(column=1, row=1, padx=10, pady=10, columnspan=3, rowspan=2)
        button_calc = ttk.Button(self.offset_frame, text="calculate", command=self.calculateOffset)
        button_calc.grid(column=9, row=1, padx=5, pady=10, columnspan=1, rowspan=2)

        self.createSingleOffsetWidgetInput()
        self.createSingleOffsetWidgetBtn()

    def createSingleOffsetWidgetInput(self):
        if self.offset_manipulation_status[0] == "non_edit":
            self.label = ttk.Label(self.offset_frame, text=f"({round(float(self.offset_manipulation_values[0][0].get()), 2)},{round(float(self.offset_manipulation_values[0][1].get()), 2)})", width=15)
            self.label.grid(column=2, row=3, padx=10, pady=5, columnspan=2, rowspan=2)
        else:
            element1 = tk.Entry(self.offset_frame, textvariable=self.offset_manipulation_values[0][0],font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color, width=7)
            element1.grid(column=1, row=3, padx=5, pady=5, columnspan=2, rowspan=2)
            element2 = tk.Entry(self.offset_frame, textvariable=self.offset_manipulation_values[0][1],font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color, width=7)
            element2.grid(column=3, row=3, padx=0, pady=5, columnspan=2, rowspan=2)

        self.label = ttk.Label(self.offset_frame, text="to", width=5)
        self.label.grid(column=5, row=3, padx=10, pady=0, columnspan=1, rowspan=2)

        if self.offset_manipulation_status[1] == "non_edit":
            self.label = ttk.Label(self.offset_frame, text=f"({round(float(self.offset_manipulation_values[1][0].get()), 2)},{round(float(self.offset_manipulation_values[1][1].get()), 2)})", width=15)
            self.label.grid(column=8, row=3, padx=10, pady=5, columnspan=2, rowspan=2)
        else:
            element3 = tk.Entry(self.offset_frame, textvariable=self.offset_manipulation_values[1][0], font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color, width=7)
            element3.grid(column=8, row=3, padx=0, pady=5, columnspan=1, rowspan=2)
            element4 = tk.Entry(self.offset_frame, textvariable=self.offset_manipulation_values[1][1], font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color, width=7)
            element4.grid(column=9, row=3, padx=0, pady=5, columnspan=1, rowspan=2)

    def updateOffsetWidget(self,i,status):
        if status == "non_edit":
            if self.offsetInputTest(i):
                self.offset_manipulation_status[i] = status
                self.baselineWidget()
        else:
            self.offset_manipulation_status[i] = status
            self.baselineWidget()

    def createSingleOffsetWidgetBtn(self):
        if self.offset_manipulation_status[0] == "non_edit":
            button_edit = ttk.Button(self.offset_frame, text="edit", command=lambda: self.updateOffsetWidget(0,"edit"))
            button_edit.grid(column=2, row=5, padx=5, pady=0, columnspan=1, rowspan=2)
        if self.offset_manipulation_status[0] == "edit":
            button_save = ttk.Button(self.offset_frame, text="save", command=lambda: self.updateOffsetWidget(0,"non_edit"))
            button_save.grid(column=2, row=5, padx=5, pady=0, columnspan=1, rowspan=2)
        button_get_1 = ttk.Button(self.offset_frame, text="get value", command=lambda: self.offsetGetValue(0))
        button_get_1.grid(column=3, row=5, padx=5, pady=0, columnspan=1, rowspan=2)

        if self.offset_manipulation_status[1] == "non_edit":
            button_edit = ttk.Button(self.offset_frame, text="edit", command=lambda: self.updateOffsetWidget(1,"edit"))
            button_edit.grid(column=8, row=5, padx=5, pady=0, columnspan=1, rowspan=2)
        if self.offset_manipulation_status[1] == "edit":
            button_save = ttk.Button(self.offset_frame, text="save", command=lambda: self.updateOffsetWidget(1,"non_edit"))
            button_save.grid(column=8, row=5, padx=5, pady=0, columnspan=1, rowspan=2)
        button_get_2 = ttk.Button(self.offset_frame, text="get value", command=lambda: self.offsetGetValue(1))
        button_get_2.grid(column=9, row=5, padx=5, pady=0, columnspan=1, rowspan=2)

    def offsetGetValue(self,i):
        if session_cache.graphvalue_baseline != "N.A.":
            self.offset_manipulation_values[i][0].set(session_cache.graphvalue_baseline[0])
            self.offset_manipulation_values[i][1].set(session_cache.graphvalue_baseline[1])
            #print(self.offset_manipulation_values)
            self.offset_manipulation_status[i] = "non_edit"
            self.baselineWidget()

    def offsetInputTest(self,i):
        input_check_bool = True
        text = 'please check the input of\n'
        for element in self.offset_manipulation_values[i]:
            if str(element.get()) != "empty":
                if len(str(element.get())) == 0:
                    input_check_bool = False
                    text = text + 'value not specified\n'
                else:
                    try:
                        float(element.get())
                    except ValueError:
                        text = text + f'{element.get()} is not a number\n'
                        input_check_bool = False
        if not input_check_bool:
            self.showInfo(text)
        return input_check_bool

    def createAsymmetricLeastSquaresBaselineWidget(self):
        self.als_baseline_frame = tk.Frame(self.baseline_frame, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)
        self.als_baseline_frame.pack(expand=1, fill="both", padx=10, pady=10, side='top')
        self.als_baseline_frame.propagate(0)

        self.label = ttk.Label(self.als_baseline_frame, text="Asymmetric Least Squares Baseline")
        self.label.grid(column=1, row=1, padx=10, pady=10, columnspan=5, rowspan=2)
        button_calc = ttk.Button(self.als_baseline_frame, text="calculate", command=self.calculateALSBaseline)
        button_calc.grid(column=7, row=1, padx=5, pady=10, columnspan=1, rowspan=2)

        self.createSingleALSBaselineWidgetP()
        self.createSingleALSBaselineWidgetLambda()

        self.createSingleALSBaselineWidgetBtn()

    def createSingleALSBaselineWidgetP(self):
        label = ttk.Label(self.als_baseline_frame, text="p:", width=17)
        label.grid(column=1, row=3, padx=10, pady=5, columnspan=4, rowspan=2)
        if self.als_manipulation_status[0] == "non_edit":
            label = ttk.Label(self.als_baseline_frame, text=f"{self.als_manipulation_values[0].get()}", width=10)
            label.grid(column=3, row=3, padx=10, pady=0, columnspan=4, rowspan=2)
        else:
            element = tk.Entry(self.als_baseline_frame, textvariable=self.als_manipulation_values[0],font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color, width=12)
            element.grid(column=3, row=3, padx=10, pady=0, columnspan=4, rowspan=2)

    def createSingleALSBaselineWidgetLambda(self):
        label = ttk.Label(self.als_baseline_frame, text="Lambda:", width=17)
        label.grid(column=1, row=7, padx=10, pady=5, columnspan=4, rowspan=2)
        if self.als_manipulation_status[1] == "non_edit":
            label = ttk.Label(self.als_baseline_frame, text=f"{self.als_manipulation_values[1].get()}", width=10)
            label.grid(column=3, row=7, padx=10, pady=0, columnspan=4, rowspan=2)
        else:
            element = tk.Entry(self.als_baseline_frame, textvariable=self.als_manipulation_values[1],font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color, width=12)
            element.grid(column=3, row=7, padx=10, pady=0, columnspan=4, rowspan=2)

    def createSingleALSBaselineWidgetBtn(self):
        if self.als_manipulation_status[0] == "non_edit":
            button_edit = ttk.Button(self.als_baseline_frame, text="edit", command=lambda: self.updateALSWidget(0,"edit"))
            button_edit.grid(column=7, row=3, padx=10, pady=0, columnspan=1, rowspan=2)
        if self.als_manipulation_status[0] == "edit":
            button_save = ttk.Button(self.als_baseline_frame, text="save", command=lambda: self.updateALSWidget(0,"non_edit"))
            button_save.grid(column=7, row=3, padx=10, pady=0, columnspan=1, rowspan=2)

        if self.als_manipulation_status[1] == "non_edit":
            button_edit = ttk.Button(self.als_baseline_frame, text="edit", command=lambda: self.updateALSWidget(1,"edit"))
            button_edit.grid(column=7, row=7, padx=10, pady=0, columnspan=1, rowspan=2)
        if self.als_manipulation_status[1] == "edit":
            button_save = ttk.Button(self.als_baseline_frame, text="save", command=lambda: self.updateALSWidget(1,"non_edit"))
            button_save.grid(column=7, row=7, padx=10, pady=0, columnspan=1, rowspan=2)

    def updateALSWidget(self,i,status):
        if status == "non_edit":
            if self.alsInputTest(i):
                self.als_manipulation_status[i] = status
                self.baselineWidget()
        else:
            self.als_manipulation_status[i] = status
            self.baselineWidget()

    def alsInputTest(self,i):
        input_check_bool = True
        text = 'please check the input of\n'
        if len(str(self.als_manipulation_values[i].get())) == 0:
            input_check_bool = False
            text = text + 'value not specified\n'
        else:
            try:
                float(self.als_manipulation_values[i].get())
            except ValueError:
                text = text + f'{self.als_manipulation_values[i].get()} is not a number\n'
                input_check_bool = False
        if not input_check_bool:
            self.showInfo(text)
        return input_check_bool

    def createCurrentBaselineWidget(self):
        self.current_baseline_frame = tk.Frame(self.baseline_frame, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)
        self.current_baseline_frame.pack(expand=1, fill="both", padx=10, pady=10, side='top')
        self.current_baseline_frame.propagate(0)

        self.label = ttk.Label(self.current_baseline_frame, text="Current Baseline")
        self.label.grid(column=1, row=1, padx=10, pady=10, columnspan=3, rowspan=2)


    def initOffsetManiVars(self):
        var_11 = tk.StringVar(self.baseline_frame)
        var_11.set(0)
        var_12 = tk.StringVar(self.baseline_frame)
        var_12.set(0)
        var_21 = tk.StringVar(self.baseline_frame)
        var_21.set(0)
        var_22 = tk.StringVar(self.baseline_frame)
        var_22.set(0)
        self.offset_manipulation_values[0][0] = var_11
        self.offset_manipulation_values[0][1] = var_12
        self.offset_manipulation_values[1][0] = var_21
        self.offset_manipulation_values[1][1] = var_22

    def initALSManiVars(self):
        var_1 = tk.StringVar(self.baseline_frame)
        var_1.set(self.als_manipulation_values[0])
        var_2 = tk.StringVar(self.baseline_frame)
        var_2.set(self.als_manipulation_values[1])
        self.als_manipulation_values = [var_1,var_2]

    def initJumpVars(self):
        var = tk.StringVar(self.jump_frame)
        var.set("N.A.")
        self.jump_manipulation_values = var

    def calculateOffset(self):
        x1 = float(self.offset_manipulation_values[0][0].get())
        x2 = float(self.offset_manipulation_values[1][0].get())
        y1 = float(self.offset_manipulation_values[0][1].get())
        y2 = float(self.offset_manipulation_values[1][1].get())

        if x1 == x2 and y1 == y2:
            self.constantOffset(y1)
        else:
            offset = []
            data_with_offset = []
            m = (y1-y2) / (x2-x1)
            for element in session_cache.original_data_wo_baseline:
                y_value = ((x1 - element[0])*m) + y1
                offset.append([element[0],y_value])
                data_with_offset.append([element[0],element[1]-y_value])
            session_cache.current_offset = [offset,data_with_offset]
            self.showCurrentBaselinePlot(True)

    def constantOffset(self, constant):
        offset = []
        data_with_offset = []
        for element in session_cache.original_data_wo_baseline:
            offset.append([element[0], constant])
            data_with_offset.append([element[0], element[1] - constant])
        session_cache.current_offset = [offset, data_with_offset]
        self.showCurrentBaselinePlot(True)

    def sortAndUniq(self, input):
        output = []
        new_x_values = []
        for element in input:
            if element[0] not in new_x_values:
                new_x_values.append(element[0])
                output.append(element)

        output.sort(key=lambda tup: tup[0])
        return output

    def baseline_als_optimized(self, y, niter=10):
        L = len(y)
        D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
        D = float(self.als_manipulation_values[1].get()) * D.dot(D.transpose())  # Precompute this term since it does not depend on `w`
        w = np.ones(L)
        W = sparse.spdiags(w, 0, L, L)
        p = float(self.als_manipulation_values[0].get())
        for i in range(niter):
            W.setdiag(w)  # Do not create a new matrix, just update diagonal values
            Z = W + D
            z = spsolve(Z, w * y)
            w = p * (y > z) + (1 - p) * (y < z)
        return z

    def calculateALSBaseline(self):
        #print(session_cache.original_data_wo_baseline)
        session_cache.original_data_wo_baseline = self.sortAndUniq(session_cache.original_data_wo_baseline)
        f = CubicSpline([x[0] for x in session_cache.original_data_wo_baseline], [x[1] for x in session_cache.original_data_wo_baseline],bc_type='natural')
        minimum =int(min([x[0] for x in session_cache.original_data_wo_baseline]))
        maximum = int(max([x[0] for x in session_cache.original_data_wo_baseline]))

        x_value = []
        y_value = []

        for x in range(0, maximum - minimum):
            y_value.append(f(minimum + x))
            x_value.append(minimum + x)
        y_value = self.baseline_als_optimized(y_value)
        offset = []
        data_with_offset = []
        f = CubicSpline(x_value, y_value, bc_type='natural')
        for element in session_cache.original_data_wo_baseline:
            offset.append([element[0],float(f(element[0]))])
            data_with_offset.append([element[0],element[1] - f(element[0])])
        session_cache.current_offset = [offset, data_with_offset]
       #print(session_cache.current_offset)
        self.showCurrentBaselinePlot(True)


    def confirm(self):
        session_cache.confirmed_offset = session_cache.current_offset
        session_cache.original_data = session_cache.current_offset[1]
        self.showCurrentBaselinePlot(False)

    def decline(self):
        session_cache.current_offset = [[[400, 0], [850, 0]],[[400, 0], [850, 0]]]
        self.showCurrentBaselinePlot(False)

    def showInfo(self, text):
        showinfo(
            title='Wrong Input',
            message=text
        )

    def passing(self):
        pass






