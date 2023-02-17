
from lmfit import minimize, Parameters, Minimizer, fit_report
from scipy.interpolate import CubicSpline
import pickle
import numpy as np



class Session():

    def __init__(self):
        self.graphvalue = "N.A."
        self.graphvalue_baseline = "N.A."
        self.referencespectra_list = [[],[],[],[],[]]
        self.modified_referencespectra_list = [[],[],[],[],[]]
        self.referencespectra_list_ids = [[-1,"N.A."],[-1,"N.A."],[-1,"N.A."],[-1,"N.A."],[-1,"N.A."]]
        self.data = [[400,0],[850,0]]
        self.confirmed_offset = []
        self.current_offset = [[[400, 0], [850, 0]],[[400, 0], [850, 0]]]
        self.original_data_wo_jumps_baseline = [[400,0],[850,0]]
        self.original_data_wo_baseline = [[400,0],[850,0]]
        self.current_jump = [0,0,[[400,0],[850,0]]]
        self.original_data = [[400,0],[850,0]]
        self.fitted_data = [[400,0]]
        self.fitted_data_residuum = [[400,0]]
        self.fitted_params_wo_polynom = [["placeholder", 0], [1, 0], [2, 0], [3, 0], [4, 0]]
        self.fitted_params = [["placeholder",0],[1,0],[2,0],[3,0],[4,0]]
        self.run_index = 0
        self.omitted_areas = [[0,0,False],[0,0,False],[0,0,False]]
        self.fit_start_end = [0,10000,False]
        self.datajumps = []
        self.fitable_border = [0,10000]
        self.fit_param_names_wo_polynom = ['PUIII', 'PUIV', 'PUV', 'PUVI', 'PUColl']
        self.fit_param_names = ['PUIII','PUIV','PUV','PUVI','PUColl'] #'Pu(III)','Pu(IV)','Pu(V)','Pu(VI)','PuColl'
        self.fit_params = None
        self.fit_params_polynom = []
        self.fit_polynomial_degree = 3
        self.fit_polynomial_degree_max=15
        self.polynom_data = [[400, 0], [850, 0]]
        self.fit_params_values = [[0.5,0.0,"empty",True],[0.5,0.0,"empty",True],[0.5,0.0,"empty",True],[0.5,0.0,"empty",True],[0.5,0.0,"empty",True]]

        self.setFitParams()
        self.covar_error = False
        self.covar_error_list = []
        self.covar_matrix = None
        self.graph_creator_graph_list = []
        self.graph_code_list = []

        self.id = 0
        self.name = 'testname'
        self.filename = None
        self.cuvette_size = None
        self.normalization_value = 1
        self.concentration = 1
        self.solution = None
        self.save_date = None

        self.saved = False
        self.fitted = False

    def reset(self):
        self.__init__()

    def sortAndUniq(self, input):
        output = []
        new_x_values = []
        for element in input:
            if element[0] not in new_x_values:
                new_x_values.append(element[0])
                output.append(element)

        output.sort(key=lambda tup: tup[0])
        return output

    def load_ref_spectra_list(self):
        open_file = open('reference_spectra/sys/reference_spectra_list.dat', "rb")
        try:
            loaded_obj = pickle.load(open_file)
        except:
            loaded_obj = []
        open_file.close()
        return loaded_obj

    def updateRefSpectraList(self):
        all_spectras = self.load_ref_spectra_list()
        for spectrum in all_spectras:
            i = 0
            for element in self.referencespectra_list_ids:
                if element[0] == spectrum.id:
                    self.referencespectra_list[i] = [spectrum.id,spectrum.referencespectra_measurements,float(spectrum.normalization_value),float(spectrum.cuvette_size)]
                i += 1

    def updateFitableBorder(self):

        self.fitable_border[0] = min(self.original_data)[0]
        self.fitable_border[1] = max(self.original_data)[0]

        if self.fit_start_end[2]:
            if self.fitable_border[0] < self.fit_start_end[0]:
                self.fitable_border[0] = self.fit_start_end[0]
            if self.fitable_border[1] > self.fit_start_end[1]:
                self.fitable_border[1] = self.fit_start_end[1]

    def prepareData(self):
        data = []
        for element in self.original_data:
            if self.fitable_border[0] <= element[0] and self.fitable_border[1] >= element[0]:
                data.append([element[0], element[1] * float(self.cuvette_size) / float(self.normalization_value)])
                data = self.implementOmittedAreas(data)
        self.data = data

    def implementOmittedAreas(self, data):
        list = data
        for element in self.omitted_areas:
            if element[2]:
                list = self.implementSingleOmittedArea(list, element)
        return list

    def implementSingleOmittedArea(self,data, omitted_area):
        list = []
        for element in data:
            if element[0] >= float(omitted_area[1]) or element[0] <= float(omitted_area[0]):
                list.append([element[0],element[1]])
        return list

    def prepareRefSpectra(self):
        i = 0

        for list in self.referencespectra_list:
            x = []
            y = []
            list[1] = self.sortAndUniq(list[1])
            for element in list[1]:
                x.append(element[0])
                #HERE QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ  cuvette_size und norm.-faktor ref data QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ
                y.append((element[1]/list[2])*list[3])

            f = CubicSpline(x, y, bc_type='natural')

            new_list = []
            for element in self.data:
                y_value = f(element[0])
                if y_value < 0 or min(list[1])[0] > element[0] or max(list[1])[0] < element[0]:
                    y_value = 0

                new_list.append([element[0], y_value])

            self.modified_referencespectra_list[i] = new_list

            i += 1

    def printFitParams(self):
        print(self.fitted_params)

    def fit(self):
        self.setFitParams()
        self.updateRefSpectraList()
        self.updateFitableBorder()
        self.prepareData()
        self.prepareRefSpectra()
        self.covar_error = False

        out = minimize(self.fitFunction, self.fit_params, scale_covar=False, calc_covar=True)
        #print(fit_report(out))

        res_list = self.fitFunction(out.params)


        i = 0
        for element in self.fit_param_names:
            value = float(out.params.valuesdict()[self.fit_param_names[i]])
            if value < 0 and value > -0.00001:
                value = 0
            self.fitted_params[i] = [i,value]
            self.fitted_params_wo_polynom[i] = [i, value]
            i += 1


        try:
            self.covar_matrix = out.covar
        except Exception as e:
            self.covar_error = True
            self.checkBoundaries(out)

        #print('fitted_params: ')
        for n in range(0, self.fit_polynomial_degree):
            value = float(out.params.valuesdict()[f'polynom_param_{n}'])
            self.fitted_params[i] = [i,value]
            i += 1

        plot_list = []
        plot_list_residuum = []
        i = 0
        for element in self.data:
            plot_list.append([element[0], self.singleFitFuncElement(i)]) #res_list[i] + element[1]])
            plot_list_residuum.append([element[0], res_list[i]])
            i += 1


        self.fitted_data = plot_list
        self.fitted_data_residuum = plot_list_residuum
        self.fitted = True
        self.setPolynominalData()

        self.run_index = 0



    def checkBoundaries(self, out):
        self.covar_error_list = []
        if isinstance(out, Parameters):
            result, params = None, out
        if hasattr(out, 'params'):
            result = out
            params = out.params
        if result is not None:
            #print("##  Warning: uncertainties could not be estimated:")
            parnames_varying = [par for par in result.params
                                if result.params[par].vary]
            for name in parnames_varying:
                par = params[name]
                #print(par)
                if par.init_value and np.allclose(par.value, par.init_value):
                    #print('    %s:  at initial value' % (name))
                    self.covar_error_list.append([par,'at initial value'])
                if (np.allclose(par.value, par.min) or np.allclose(par.value, par.max)):
                    #print('    %s:  at boundary' % (name))
                    self.covar_error_list.append([par, 'at boundary'])
        #print(self.covar_error_list)

    def singleFitFuncElement(self, x):
        pu3 = self.fitted_params[0][1]
        pu4 = self.fitted_params[1][1]
        pu5 = self.fitted_params[2][1]
        pu6 = self.fitted_params[3][1]
        puColl = self.fitted_params[4][1]
        polynom_value = 0

        for n in range(0, self.fit_polynomial_degree):
            polynom_value += self.fitted_params[5 + n][1] * self.data[x][0] ** n

        return polynom_value\
                + pu3 * self.modified_referencespectra_list[0][x][1] \
                + pu4 * self.modified_referencespectra_list[1][x][1] \
                + pu5 * self.modified_referencespectra_list[2][x][1] \
                + pu6 * self.modified_referencespectra_list[3][x][1] \
                + puColl * self.modified_referencespectra_list[4][x][1]

    def fitFunction(self,params):
        pu3 = params['PUIII']
        pu4 = params['PUIV']
        pu5 = params['PUV']
        pu6 = params['PUVI']
        puColl = params['PUColl']

        self.run_index = self.run_index + 1
        y_model = []
        i = 0
        #print("run index:",self.run_index)
        for element in self.data:

            polynom_value = 0
            for n in range(0, self.fit_polynomial_degree):
                polynom_value += params[f'polynom_param_{n}'] * element[0] ** n

            y_model_element = element[1] - polynom_value\
                -(pu3 * self.modified_referencespectra_list[0][i][1] \
                + pu4 * self.modified_referencespectra_list[1][i][1] \
                + pu5 * self.modified_referencespectra_list[2][i][1] \
                + pu6 * self.modified_referencespectra_list[3][i][1] \
                + puColl * self.modified_referencespectra_list[4][i][1])

            y_model.append(y_model_element)
            i += 1
        return y_model

    def polynomCalcWParams(self, params, x):
        polynom_value = 0
        #print(params)
        for n in range(0, self.fit_polynomial_degree):
            polynom_value += params[f'polynom_param_{n}'] * x ** n
        return polynom_value

    def polynomCalc(self, x):
        polynom_value = 0
        #print(params)
        for n in range(0, self.fit_polynomial_degree):
            #print(n, self.fitted_params[5 + n])
            polynom_value += self.fitted_params[5 + n][1] * x ** n
            #print("POLY",x)
        return polynom_value


    def setPolynominalData(self):
        if self.fit_polynomial_degree > 0:
            self.polynom_data = []
            #print("fittedData:", self.fitted_data)
            for element in self.fitted_data:
                self.polynom_data.append([element[0] , self.polynomCalc(element[0])])
        else:
            self.polynom_data = [[400, 0], [850, 0]]
        #print(self.polynom_data)

    def setFitParams(self):
        self.fit_params = Parameters()
        self.fitted_params = [["placeholder",0],[1,0],[2,0],[3,0],[4,0]]
        self.fit_param_names = ['PUIII','PUIV','PUV','PUVI','PUColl']
        i=0
        for element in self.fit_params_values:
            self.fit_params.add(self.fit_param_names[i])
            if element[0] != "empty" and element[0] != "":
                self.fit_params[self.fit_param_names[i]].set(value=float(element[0]))
            if element[1] != "empty":
                self.fit_params[self.fit_param_names[i]].set(min=float(element[1]))
            if element[2] != "empty":
                self.fit_params[self.fit_param_names[i]].set(max=float(element[2]))
            self.fit_params[self.fit_param_names[i]].set(vary=bool(int(element[3])))
            #print(element[3])
            #print(bool(int(element[3])))
            i += 1


        for p in range(0, self.fit_polynomial_degree):
            self.fit_params.add(f"polynom_param_{p}")
            self.fit_params[f"polynom_param_{p}"].set(value=0.0005)
            self.fitted_params.append([5 + p,0])
            #self.fit_param_names.append(f"polynom_param_{p}")

    def printAll(self):
        print(f"ori. data:{self.original_data}\n data:{self.data}")
        self.printFitData()
        self.printCurrentSpectrum()

    def printFitData(self):
        print("Fit:")
        print(f"Ref IDs: {self.referencespectra_list_ids}")
        print(f"start:{self.fit_start_end[0]} - end:{self.fit_start_end[1]}")
        self.printOmittedAreas()

    def printOmittedAreas(self):
        for element in self.omitted_areas:
            print(f"start:{element[0]} - end:{element[1]}; consideration:{element[2]}")

    def printCurrentSpectrum(self):
        print("Test ID:%s name:%s cuvette_size:%s concentration_value:%s solution:%s name:%s" % (
        self.id, self.name, self.cuvette_size, self.concentration, self.solution, self.name))
        print(self.filename)

    def printMinimizerResult(self, result):
        print(f"Result: /n status: {result.status}")
        print(f"success: {result.success}")
        print(f"errorbars: {result.errorbars}")
        print(f"errormessage: {result.message}")
        print(f"lmdif_message: {result.lmdif_message}")

session_cache = Session()



class CurrentReferenceSpectra():
    # concentration = normalization_value
    def __init__(self):
        self.id = -1
        self.name = 'testname'
        self.filename = None
        self.type = None
        self.edges = []
        self.cuvette_size = None
        self.normalization_value = 1  #concentration
        self.solution = None
        self.save_date = None
        self.referencespectra_measurements = [[400,0],[850,0]]
        self.saved = False

    def reset(self):
        self.__init__()

    def printCurrentRefSpectrum(self):
        print("<Test ID:%s name:%s type:%s cuvette_size:%s concentration_value:%s solution:%s name:%s>" % (self.id, self.name, self.type, self.cuvette_size, self.normalization_value, self.solution, self.name))
        print(self.referencespectra_measurements)
        print(self.filename)

    def createDescriptionName(self):
        name = self.name + '(' + str(self.solution) + ')'
        return name

current_reference_spectrum = CurrentReferenceSpectra()



class CurrentAnalysis():
    def __init__(self):

        self.name = 'testname'
        self.filename = None
        self.save_date = None
        self.saved = False
        self.current_data_key = 'Fit'

        self.graph_labels = ['Fit', 'Pu(III)', 'Pu(IV)', 'Pu(V)', 'Pu(VI)', 'PuColl', 'Polynom', 'Data', 'Residuum']
        self.data_list = []


    def addSingleData(self, session_data):
        new_data = self.fillSingleData(session_data)
        self.data_list.append(new_data)

    def fillSingleData(self, data):
        new_data = SingleDataAnalysis()
        new_data.cuvette_size = data.cuvette_size
        new_data.normalization_value = data.normalization_value
        new_data.concentration = data.concentration
        new_data.solution = data.solution
        new_data.fitted_params = data.fitted_params
        new_data.fit = data.fitted_data
        new_data.original_data = data.data
        new_data.fitted_data_residuum = data.fitted_data_residuum
        new_data.polynom_data = data.polynom_data
        new_data.modified_referencespectra_list = data.modified_referencespectra_list
        new_data.name = data.name
        return new_data

    def getAllGraphData(self):
        fit_list = []
        for element in self.data_list:
            fit_list.append(self.getSingleData(element))
        return fit_list

    def getSingleData(self, single_data):
        data, param = self.getDataFromKey(single_data)
        single_graph_data = []
        i = 0
        for element in data:
            try:
                value = [element[0], element[1] * param]
                single_graph_data.append(value)
            except:
                single_graph_data.append([element[0], 0])
            i += 1

        return single_graph_data

    def getDataFromKey(self, single_data):
        if(self.current_data_key == self.graph_labels[0]):
            return [single_data.fit,1]
        elif(self.current_data_key == self.graph_labels[1]):
            return [single_data.modified_referencespectra_list[0],single_data.fitted_params[0][1]]
        elif(self.current_data_key == self.graph_labels[2]):
            return [single_data.modified_referencespectra_list[1],single_data.fitted_params[1][1]]
        elif(self.current_data_key == self.graph_labels[3]):
            return [single_data.modified_referencespectra_list[2],single_data.fitted_params[2][1]]
        elif(self.current_data_key == self.graph_labels[4]):
            return [single_data.modified_referencespectra_list[3],single_data.fitted_params[3][1]]
        elif(self.current_data_key == self.graph_labels[5]):
            return [single_data.modified_referencespectra_list[4],single_data.fitted_params[4][1]]
        elif (self.current_data_key == self.graph_labels[6]):
            return [single_data.polynom_data, 1]
        elif (self.current_data_key == self.graph_labels[7]):
            return [single_data.original_data, 1]
        elif (self.current_data_key == self.graph_labels[8]):
            return [single_data.fitted_data_residuum, 1]
        else:
            print('error: 00518')

    def reset(self):
        self.__init__()

current_analysis = CurrentAnalysis()



class SingleDataAnalysis():
    def __init__(self):
        self.name = 'noName'
        self.filename = None
        self.filepath = None
        self.save_date = None

        self.cuvette_size = None
        self.normalization_value = 1
        self.concentration = 1
        self.solution = None

        self.fitted_params = [["placeholder",0],[1,0],[2,0],[3,0],[4,0]]
        self.fit = [[400, 0], [850, 0]]
        self.original_data = [[400, 0], [850, 0]]
        self.fitted_data_residuum = [[400, 0], [850, 0]]
        self.polynom_data = [[400, 0], [850, 0]]
        self.modified_referencespectra_list = [[[400, 0], [850, 0]],[[400, 0], [850, 0]],[[400, 0], [850, 0]],[[400, 0], [850, 0]],[[400, 0], [850, 0]]]


