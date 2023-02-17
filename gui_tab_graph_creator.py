import tkinter as tk
from tkinter import ttk
from session_cache import session_cache, current_reference_spectrum
from gui_plot_widget import GraphWidget
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

class TabGraphCreator(tk.Frame):

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        self.main_frame = tk.Frame(self, bg=design_scheme.bg_color)
        self.main_frame.pack(expand=1, fill="both", padx=20, pady=20)
        #self.frame.propagate(0)

        self.graph_manipulation_frame = tk.Frame(self.main_frame, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)
        self.graph_manipulation_frame.pack(expand=1, fill="both", padx=10, pady=10, side='right')
        self.graph_manipulation_frame.propagate(0)

        self.graph_frame = tk.Frame(self.main_frame, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)
        self.graph_frame.pack(expand=1, fill="both", padx=10, pady=10, side='right')
        self.graph_frame.propagate(0)
        self.graph_plot_widget = GraphWidget(self.graph_frame, "graph creator results")

        self.graph_collection_frame = tk.Frame(self.main_frame, background=design_scheme.bg_color, highlightbackground=design_scheme.border_color, highlightthickness=design_scheme.h_thickness, bd=0)
        self.graph_collection_frame.pack(expand=1, fill="both", padx=10, pady=10, side='right')
        self.graph_collection_frame.propagate(0)

        self.current_graph_code = ''
        self.current_math_operation = ''
        self.graph_labels = ['Fit', 'Pu(III)', 'Pu(IV)', 'Pu(V)', 'Pu(VI)', 'PuColl', 'Polynom', 'Data', '+', '-']
        self.btn_list_graphs = []

        self.widgetListCodeEntry=[]
        #self.codeEntry = tk.Text(self.graph_manipulation_frame, width=38, font=('Helvetica', 9, 'bold'), foreground=design_scheme.bg_color, height= 5)

        self.lable_output = ttk.Label(self.graph_manipulation_frame, text="Please fit or load fitted data", anchor="w", width= 34 , foreground='red')
        self.lable_output.grid(column=0, row=80, padx=0, pady=10, columnspan=29, rowspan=2)

        self.createGraphBtn()
        self.createGraphCodeOut()
        self.createGraphInputfield()
        self.generateGraphCollection()
        self.disableWidget()




    def createGraphInputfield(self):
        self.widgetListCodeEntry.append(tk.Text(self.graph_manipulation_frame, width=38, font=('Helvetica', 9, 'bold'),foreground=design_scheme.bg_color, height=5))
        self.widgetListCodeEntry[0].grid(column=0, row=150, padx=0, pady=(20,5), columnspan=29, rowspan=2)
        #self.widgetListCodeEntry.append(ttk.Button(self.graph_manipulation_frame, width=12, text="save", command= self.saveCodeInput))
        #self.widgetListCodeEntry[1].grid(column=0, row=170, padx=(20,0), pady=10, columnspan=1, rowspan=2)
        #self.widgetListCodeEntry.append(ttk.Button(self.graph_manipulation_frame, width=12, text="info", command=self.showCodeInfo))
        #self.widgetListCodeEntry[2].grid(column=10, row=170, padx=(20,0), pady=10, columnspan=1, rowspan=2)

    def saveCodeInput(self):
        input = self.widgetListCodeEntry[0].get("1.0","end")
        if len(session_cache.graph_code_list) < 7:
            if self.validateGraphCode(input):
                self.current_graph_code = input
                session_cache.graph_code_list.append(input)
                session_cache.graph_creator_graph_list.append(self.codeToGraph(input))
                self.clearGraphCode()
                self.updateGraph()
                self.generateGraphCollection()
                self.current_graph_code = ''
                self.widgetListCodeEntry[0].delete("1.0", "end")
            else:
                self.showAlert("error: invalid graph code")
        else:
            self.showAlert("error: maximum number of graphs (7) reached")


    def addToGraphCode(self,input):
        if(input == '-' or input == '+'):
            self.current_math_operation = input
            self.deactivateAndActivateGraphBtn(self.btn_list_graphs[0:8],self.btn_list_graphs[8:10])
        else:

            self.deactivateAndActivateGraphBtn(self.btn_list_graphs[8:10], self.btn_list_graphs[0:8])
            if(len(self.current_graph_code) > 0):
                self.current_graph_code = self.current_graph_code + '%' + self.current_math_operation + '&' + input
            else:
                self.current_graph_code = input

        self.lable_output['text'] = textwrap.fill(f"{self.graphCodeReadable()}", width=25)

    def validateGraphCode(self,code):
        list = code.split('%')
        valid = True
        msg = ""
        if list[0] not in self.graph_labels[:7]:
            valid = False
            msg = "not in self.graph_labels[:7]"
        for element in list[1:]:
            single_element = element.split('&')
            if single_element[0] not in self.graph_labels[7:] and single_element[1] not in self.graph_labels[:7]:
                valid = False
                msg += 'not in self.graph_labels[7:] and single_element[1] not in self.graph_labels[:7]'
        #print('valid:', valid , msg)
        return valid

    def graphCodeReadable(self):
        text = 'Graph: '
        list = self.current_graph_code.split('%')
        text += list[0]
        for element in list[1:]:
            single_element = element.split('&')
            for part in single_element:
                text += part
        return text

    def generateGraphCollection(self):
        for widget in self.graph_collection_frame.winfo_children():
            widget.destroy()
        label = ttk.Label(self.graph_collection_frame, text=f"Graphs", width=40)
        label.grid(column=10, row=10 , padx=10, pady=10, columnspan=20, rowspan=2)
        for x in range(len(session_cache.graph_code_list)):
            self.graphCodeForManipulationLine(x)

    def graphCodeForManipulationLine(self, i):
        text = textwrap.fill(f"{self.graphCodeForManipulationLineText(i)}", width=25)
        label = ttk.Label(self.graph_collection_frame, anchor="w", text=text, width=25)
        label.grid(column=10, row=10 * (i + 2 ), padx=(20,0), pady=0, columnspan=4, rowspan=2)
        button = ttk.Button(self.graph_collection_frame, text="delete", command=lambda i = i: self.deleteGraph(i))
        button.grid(column=20, row=10 * (i + 2 ), padx=(20,0), pady=10, columnspan=1, rowspan=2)

    def deleteGraph(self, i):
        session_cache.graph_code_list.pop(i)
        session_cache.graph_creator_graph_list.pop(i)
        self.updateGraph()
        self.generateGraphCollection()

    def graphCodeForManipulationLineText(self, i):
        text = f"Graph_{i}: "
        list = session_cache.graph_code_list[i].split('%')
        text += list[0]
        for element in list[1:]:
            single_element = element.split('&')
            for part in single_element:
                text += part
        return text

    def deleteFromGraphCode(self):
        if(len(self.current_graph_code) > 0):
            list = self.current_graph_code.split('%')
            if (len(list) > 1):
                list.pop()
                self.current_graph_code = list[0]
                for element in list[1:]:
                    self.current_graph_code = self.current_graph_code + '%' + element
                self.current_math_operation = ''
                self.deactivateAndActivateGraphBtn(self.btn_list_graphs[8:10], self.btn_list_graphs[0:8])
            else:
                self.current_graph_code = ''
                self.deactivateAndActivateGraphBtn(self.btn_list_graphs[0:8],self.btn_list_graphs[8:10])
        self.lable_output['text'] = self.graphCodeReadable()

    def enableWidget(self):
        self.current_graph_code = ''
        self.current_math_operation = ''
        self.deactivateAndActivateGraphBtn(self.btn_list_graphs[0:8],self.btn_list_graphs[8:10])
        self.deactivateAndActivateGraphBtn(self.btn_list_graphs[10:], [])
        self.deactivateAndActivateGraphBtn(self.widgetListCodeEntry[1:], [])
        self.lable_output['text'] = 'Graph: '
        self.lable_output['foreground'] = design_scheme.font_color

    def disableWidget(self):
        self.current_graph_code = ''
        self.current_math_operation = ''
        self.deactivateAndActivateGraphBtn([], self.btn_list_graphs)
        self.deactivateAndActivateGraphBtn([], self.widgetListCodeEntry[1:])
        self.lable_output['foreground'] = 'red'
        self.lable_output['text'] = "Please fit or load fitted data"
        self.updateGraph()
        self.generateGraphCollection()

    def clearGraphCode(self):
        self.current_graph_code = ''
        self.current_math_operation = ''
        self.deactivateAndActivateGraphBtn(self.btn_list_graphs[:8], self.btn_list_graphs[8:10])
        self.lable_output['text'] = "Graph: "

    def saveGraphCode(self):
        if len(session_cache.graph_code_list) < 7:
            session_cache.graph_code_list.append(self.current_graph_code)
            session_cache.graph_creator_graph_list.append(self.codeToGraph(self.current_graph_code))
            self.clearGraphCode()
            self.updateGraph()
            self.generateGraphCollection()
        else:
            self.showAlert("error: maximum number of graphs (7) reached")

    def deactivateAndActivateGraphBtn(self,listactive,listdeactive):
        for element in listactive:
            element["state"] = "enabled"
        for element in listdeactive:
            element["state"] = "disabled"

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
                self.btn_list_graphs.append(ttk.Button(self.graph_manipulation_frame, width=span, text=element, command=lambda k=k: self.addToGraphCode(self.graph_labels[k])))
                self.btn_list_graphs[k].grid(column=25, row=20 + j - 1, padx=(5, 0), pady=(10, 0), columnspan=1, rowspan=1)
            else:
                self.btn_list_graphs.append(ttk.Button(self.graph_manipulation_frame, width=span, text=element,command=lambda k=k: self.addToGraphCode(self.graph_labels[k])))
                self.btn_list_graphs[k].grid(column=i * 10, row=20 + j, padx=(20, 0), pady=(10, 0), columnspan=span, rowspan=1)

            i += 1
            k += 1
        self.deactivateAndActivateGraphBtn(self.btn_list_graphs[:8], self.btn_list_graphs[8:10])

    def createGraphCodeOut(self):

        button1 = ttk.Button(self.graph_manipulation_frame, width=12, text='clear', command=self.clearGraphCode)
        button1.grid(column=0, row=110, padx=(20,0), pady=3, columnspan=1, rowspan=1)
        self.btn_list_graphs.append(button1)
        button2 = ttk.Button(self.graph_manipulation_frame, width=12, text='return', command=self.deleteFromGraphCode)
        button2.grid(column=10, row=110, padx=(20,0), pady=3, columnspan=1, rowspan=1)
        self.btn_list_graphs.append(button2)
        button3 = ttk.Button(self.graph_manipulation_frame, width=12, text='save', command=self.saveGraphCode)
        button3.grid(column=20, row=110, padx=(20,0), pady=3, columnspan=10, rowspan=1)
        self.btn_list_graphs.append(button3)

    def codeToGraph(self,code):
        codeList = code.split('%')
        graph = self.setFirstGraph(codeList[0])
        for element in codeList[1:]:
            action = element.split('&')
            if action[0].strip() == '-':
                tmp_graph = self.getDataFromKey(action[1].strip())
                graph = self.substractGraph(graph[0],tmp_graph[0], tmp_graph[1])
            if action[0].strip() == '+':
                tmp_graph = self.getDataFromKey(action[1].strip())
                graph = self.addGraph(graph[0],tmp_graph[0], tmp_graph[1])
        return graph[0]

    def setFirstGraph(self, key):
        graph_w_factor = self.getDataFromKey(key)
        new_graph = [[],graph_w_factor[1]]
        for element in graph_w_factor[0]:
            new_graph[0].append([element[0], element[1] * graph_w_factor[1]])
        return new_graph

    def addGraph(self,graph1, graph2, factor):
        new_graph = []
        i = 0
        error = 0
        for element in graph1:
            errorbool = True
            try:
                value = [element[0], element[1] - (graph2[i][1] * factor)]
            except:
                error += 1
                errorbool = False

            if (errorbool):
                new_graph.append(value)
            else:
                new_graph.append([element[0], 0])
            i += 1

        return [new_graph, 1]

    def substractGraph(self,graph1, graph2, factor):
        new_graph = []
        i = 0
        error = 0
        for element in graph1:
            errorbool = True
            try:
                value = [element[0], element[1] - (graph2[i][1] * factor)]
            except:
                error += 1
                errorbool = False

            if(errorbool):
                new_graph.append(value)
            else:
                new_graph.append([element[0], 0])
            i += 1

        return [new_graph, 1]

    def getDataFromKey(self, key):
        if(key == self.graph_labels[0]):
            return [session_cache.fitted_data,1]
        elif(key == self.graph_labels[1]):
            return [session_cache.modified_referencespectra_list[0],session_cache.fitted_params[0][1]]
        elif(key == self.graph_labels[2]):
            return [session_cache.modified_referencespectra_list[1],session_cache.fitted_params[1][1]]
        elif(key == self.graph_labels[3]):
            return [session_cache.modified_referencespectra_list[2],session_cache.fitted_params[2][1]]
        elif(key == self.graph_labels[4]):
            return [session_cache.modified_referencespectra_list[3],session_cache.fitted_params[3][1]]
        elif(key == self.graph_labels[5]):
            return [session_cache.modified_referencespectra_list[4],session_cache.fitted_params[4][1]]
        elif (key == self.graph_labels[6]):
            return [session_cache.polynom_data, 1]
        elif (key == self.graph_labels[7]):
            return [session_cache.data, 1]
        else:
            print('error: 00518')

    def updateGraph(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_plot_widget = GraphWidget(self.graph_frame, "graph creator results")

    def showCodeInfo(self):
        showinfo(
            title='HowTo: Graphcodes',
            message='soon more! \n example: Pu(III)%-&PuColl '
        )

    def showAlert(self, text):
        showinfo(
            title='Warning',
            message=text
        )