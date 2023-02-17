import tkinter as tk
from tkinter import ttk
from session_cache import session_cache, current_reference_spectrum
from design import design_scheme
from gui_plot_widget import GraphWidget
from tkinter.messagebox import showinfo



class JumpCheck():
    def __init__(self, root, type):
        #super().__init__()
        self.root = root

        self.style = ttk.Style(self.root)
        self.style.theme_create('enlarged_graphs', parent="alt", settings=design_scheme.getDesignSettings())
        self.style.theme_use("enlarged_graphs")

        self.type = type
        self.data = []
        self.unconfirmed_jumps = []
        self.jumps = []
        self.max_dist_factor = 10
        self.jump_point = tk.StringVar(self.root)
        self.jump_point.set("")
        self.jump_found = False

        self.graph_widget_frame = tk.Frame(self.root, height=120, background=design_scheme.bg_color)
        self.graph_widget_frame.pack(expand=1, fill="both", padx=0, pady=0, side='top')
        self.jump_plot = GraphWidget(self.graph_widget_frame, "jump", True)

        self.button_widget_frame = tk.Frame(self.root, height=120, background=design_scheme.bg_color)
        self.button_widget_frame.pack(expand=1, fill="both", ipady=10, padx=0, pady=0, side='bottom')

        self.getData()


    def getData(self):
        if self.type == "jump":
            self.data = self.sortAndUniq(session_cache.original_data)
        #print(self.data)
        self.checkForJumps()

    def checkForJumps(self):
        i=0

        for element in self.data:
            if i >= 3:
                dist_1 = abs(self.data[i - 2][1] - self.data[i - 3][1])
                dist_2 = abs(self.data[i - 1][1] - self.data[i - 2][1])
                dist_3 = abs(self.data[i ][1] - self.data[i - 1][1])

                #print(self.data[i][1],self.data[i][0])
                if dist_1 != 0 and dist_2 != 0 and dist_3 != 0:
                    if dist_3 / (dist_1 + dist_2) > 20:
                        #print(self.data[i][0])
                        self.unconfirmed_jumps.append([i, [], [], 0])
                        self.jump_found = True
            i += 1

        self.buildUnconfirmedJumpsData()

    def buildUnconfirmedJumpsData(self):
        for element in self.unconfirmed_jumps:
            distance = self.data[element[0]][1] - self.data[element[0] - 1][1]
            element[3] = distance
            i = 0
            for element2 in self.data:
                y_value = self.data[i][1]
                if self.data[i][0] >= self.data[element[0]][0]:
                    y_value = y_value - distance
                element[1].append(self.data[i][0])
                element[2].append([self.data[i][0],y_value])
                i += 1
        self.confirmJumps()

    def addChoosenJump(self):
        if self.checkValue(self.jump_point.get()):
            self.jump_found = False
            if self.jumpPointTest():
                i = 0
                for element in self.data:
                    if self.data[i - 1][0] <= float(self.jump_point.get()) and self.data[i][0] >= float(self.jump_point.get()) and not self.jump_found:
                        self.unconfirmed_jumps.append([i - 1, [], [], 0])
                        self.jump_found = True
                        #print(self.unconfirmed_jumps)
                    i += 1
            self.buildUnconfirmedJumpsData()

    def jumpPointTest(self):
        test_bool = True
        text = "test:\n"
        if len(str(self.jump_point.get())) == 0:
            test_bool = False
            text = text + 'nothing entered\n'
        try:
            float(self.jump_point.get())
        except ValueError:
            text = text + f'{self.jump_point.get()} is not a number\n'
            test_bool = False
        #print(text)
        return test_bool

    def confirmJumps(self):
        if len(self.unconfirmed_jumps) != 0:
            for widget in self.graph_widget_frame.winfo_children():
                widget.destroy()
            self.jump_plot = GraphWidget(self.graph_widget_frame, "jump", True)
            self.jump_plot.plotData([self.unconfirmed_jumps[0][2], self.data], [self.data[self.unconfirmed_jumps[0][0] - 1][0]])
            self.createQuery()
        else:
            self.createEndQuery()

    def createEndQuery(self):
        for widget in self.graph_widget_frame.winfo_children():
            widget.destroy()
        self.jump_plot = GraphWidget(self.graph_widget_frame, "jump", True)
        self.jump_plot.plotData([self.data],[])

        for widget in self.button_widget_frame.winfo_children():
            widget.destroy()

        label_name = ttk.Label(self.button_widget_frame, anchor='w',width=100, text="is there any other Adjustment?")
        label_name.grid(column=1, row=0 * 10, padx=20, pady=5, columnspan=4, rowspan=2)

        button_yes = ttk.Button(self.button_widget_frame, text="yes", width=30, command=self.endQueryYes)
        button_yes.grid(column=1, row=1 * 10 + 2, padx=20, pady=0, ipadx=5, ipady=5, columnspan=1, rowspan=2)

        button_no = ttk.Button(self.button_widget_frame, text="no", width=30, command=self.endQueryNo)
        button_no.grid(column=3, row=1 * 10 + 2, padx=20, pady=0, ipadx=5, ipady=5, columnspan=1, rowspan=2)

    def endQueryYes(self):
        for widget in self.button_widget_frame.winfo_children():
            widget.destroy()

        label_name = ttk.Label(self.button_widget_frame, anchor='w',width=100, text="Please enter any wavelength value between start- and endpoint of the datajump:")
        label_name.grid(column=1, row=1, padx=20, pady=5, columnspan=4, rowspan=2)

        element = ttk.Entry(self.button_widget_frame,width=25, textvariable=self.jump_point)
        element.grid(column=4, row=1, padx=20, pady=5, columnspan=2, rowspan=2)

        button_yes = ttk.Button(self.button_widget_frame, text="Confirm", width=30, command=self.addChoosenJump)
        button_yes.grid(column=1, row=2 * 10 + 2, padx=20, pady=0, ipadx=5, ipady=5, columnspan=1, rowspan=2)

        button_no = ttk.Button(self.button_widget_frame, text="Cancel", width=30, command=self.endQueryNo)
        button_no.grid(column=3, row=2 * 10 + 2, padx=20, pady=0, ipadx=5, ipady=5, columnspan=1, rowspan=2)

    def endQueryNo(self):
        #print(self.jumps)
        session_cache.original_data_wo_baseline = session_cache.original_data
        session_cache.original_data = self.data
        session_cache.data = self.data
        for element in self.jumps:
            session_cache.datajumps.append([element[0],element[3]])
        self.root.destroy()

    def createQuery(self):

        for widget in self.button_widget_frame.winfo_children():
            widget.destroy()

        label_name = ttk.Label(self.button_widget_frame, anchor='w',width=100,text=f"Do you want to adjust the data like this at {self.data[self.unconfirmed_jumps[0][0]][0]} nm?")
        label_name.grid(column=1, row=0 * 10 + 1, padx=20, pady=5, columnspan=4, rowspan=2)

        button_yes = ttk.Button(self.button_widget_frame, text="Confirm", width=30,command=self.queryConfirm)
        button_yes.grid(column=1, row=1 * 10 + 2, padx=20, pady=0, ipadx=5, ipady=5, columnspan=1, rowspan=2)

        button_no = ttk.Button(self.button_widget_frame, text="Decline", width=30,command=self.queryDecline)
        button_no.grid(column=3, row=1 * 10 + 2, padx=20, pady=0, ipadx=5, ipady=5, columnspan=1, rowspan=2)

    def queryConfirm(self):
        self.jumps.append(self.unconfirmed_jumps[0])
        self.data = self.unconfirmed_jumps[0][2]
        self.unconfirmed_jumps.pop(0)
        self.confirmJumps()

    def queryDecline(self):
        self.unconfirmed_jumps.pop(0)
        self.confirmJumps()

    def sortAndUniq(self, input):
        output = []
        new_x_values = []
        for element in input:
            if element[0] not in new_x_values:
                new_x_values.append(element[0])
                output.append(element)

        output.sort(key=lambda tup: tup[0])
        return output

    def checkValue(self,value):
        input_check_bool = True
        text = 'please check the input:\n'
        if len(str(value)) == 0:
            text = text + f'please enter a value\n'
            input_check_bool = False
        else:
            try:
                float(value)
            except ValueError:
                text = text + f'{value} is not a number\n'
                input_check_bool = False
        if input_check_bool:
            input_check_bool, tmp_text = self.checkMinMaxForValue(float(value))
            text += tmp_text
        if not input_check_bool:
            self.showInfo(text)
        return input_check_bool

    def checkMinMaxForValue(self, value):
        min_value = min([x[0] for x in self.data])
        max_value = max([x[0] for x in self.data])
        if value >= min_value and value <= max_value:
            return True, ""
        else:
            return False, f"the input should be between {min_value} and {max_value}\n"
        #print(min([x[0] for x in self.data]))
        #print(max([x[0] for x in self.data]))

    def showInfo(self, text):
        showinfo(
            title='Wrong Input',
            message=text
        )

    def passing(self):
        pass

