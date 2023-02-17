
from lmfit import minimize, Parameters, report_fit
from scipy.interpolate import CubicSpline
import pickle




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
        self.fitted_params = [["www",0],[1,0],[2,0],[3,0],[4,0]]
        self.run_index = 0
        self.omitted_areas = [[0,0,False],[0,0,False],[0,0,False]]
        self.fit_start_end = [0,10000,False]
        self.datajumps = []
        self.fitable_border = [0,10000]
        self.fit_param_names = ['PUIII','PUIV','PUV','PUVI','PUColl']
        self.fit_params = None
        self.fit_params_values = [[0.5,-0.05,"empty",True],[0.5,-0.05,"empty",True],[0.5,-0.05,"empty",True],[0.5,-0.05,"empty",True],[0.5,-0.05,"empty",True]]
        # self.fit_param_vary_bool_list
        self.setFitParams()

        self.id = 0
        self.name = 'testname'
        self.filename = None
        self.cuvette_size = None
        self.normalization_value = None
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
        self.printOmittedAreas()
        data = []
        for element in self.original_data:
            if self.fitable_border[0] <= element[0] and self.fitable_border[1] >= element[0]:
                data.append([element[0], element[1] * float(self.cuvette_size) / float(self.normalization_value)])
                data = self.implementOmittedAreas(data)
        #HERE QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ  cuvette_size und norm.-faktor data QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ
        #HERE QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ  omitted areas fkt data QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ
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
        print(self.fit_params_values)

    def fit(self):
        self.setFitParams()
        self.updateRefSpectraList()
        self.updateFitableBorder()
        self.prepareData()
        self.prepareRefSpectra()

        out = minimize(self.fitFunction, self.fit_params)

        res_list = self.fitFunction(out.params)
        i = 0
        for element in self.fitted_params:
            value = float(out.params.valuesdict()[self.fit_param_names[i]])
            if value < 0 and value > -0.001:
                value = 0
            self.fitted_params[i] = [i,value]
            i += 1
        plot_list = []
        plot_list_residuum = []
        i = 0
        for element in self.data:
            plot_list.append([element[0],res_list[i] + element[1]])
            plot_list_residuum.append([element[0], res_list[i]])
            i += 1

        self.fitted_data = plot_list
        self.fitted_data_residuum = plot_list_residuum
        self.fitted = True


    def fitFunction(self, params):
        pu3 = params['PUIII']
        pu4 = params['PUIV']
        pu5 = params['PUV']
        pu6 = params['PUVI']
        puColl = params['PUColl']

        self.run_index = self.run_index + 1
        y_model = []
        i = 0
        for element in self.data:
            y_model_element = element[1]\
                -(pu3 * self.modified_referencespectra_list[0][i][1] \
                + pu4 * self.modified_referencespectra_list[1][i][1] \
                + pu5 * self.modified_referencespectra_list[2][i][1] \
                + pu6 * self.modified_referencespectra_list[3][i][1] \
                + puColl * self.modified_referencespectra_list[4][i][1])
            y_model.append(y_model_element)
            i += 1
        return y_model

    def setFitParams(self):
        self.fit_params = Parameters()
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
            print(element[3])
            print(bool(int(element[3])))
            i += 1

    def printAll(self):
        print(f"ori. data:{self.original_data}\n data:{self.data}")
        self.printFitData()
        self.printCurrentSpectrum()

    def printFitData(self):
        print("Fit:")
        print(f"Ref IDs: {self.referencespectra_list_ids}")
        print(f"start:{self.fit_start_end[0]} - end:{self.self.fit_start_end[1]}")
        self.printOmittedAreas()

    def printOmittedAreas(self):
        for element in self.omitted_areas:
            print(f"start:{element[0]} - end:{element[1]}; consideration:{element[2]}")

    def printCurrentSpectrum(self):
        print("Test ID:%s name:%s cuvette_size:%s normalization_value:%s solution:%s name:%s" % (
        self.id, self.name, self.cuvette_size, self.normalization_value, self.solution, self.name))
        print(self.filename)






session_cache = Session()

class CurrentReferenceSpectra():
    def __init__(self):
        self.id = -1
        self.name = 'testname'
        self.filename = None
        self.type = None
        self.edges = []
        self.cuvette_size = None
        self.normalization_value = None
        self.solution = None
        self.save_date = None
        self.referencespectra_measurements = [[400,0],[850,0]]
        self.saved = False

    def reset(self):
        self.__init__()

    def printCurrentRefSpectrum(self):
        print("<Test ID:%s name:%s type:%s cuvette_size:%s normalization_value:%s solution:%s name:%s>" % (self.id, self.name, self.type, self.cuvette_size, self.normalization_value, self.solution, self.name))
        print(self.referencespectra_measurements)
        print(self.filename)

    def createDescriptionName(self):
        name = self.name + '(' + str(self.solution) + ')'
        return name

current_reference_spectrum = CurrentReferenceSpectra()


