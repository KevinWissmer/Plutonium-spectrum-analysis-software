import csv
from pathlib import Path
from session_cache import session_cache, current_reference_spectrum
import pickle
import copy
from datetime import datetime


delete_negatives = True
delete_negatives_count = 0

def load_file (file_path, type):
    if Path(file_path).suffix == '.csv':
        load_file_csv(file_path, type)
    elif Path(file_path).suffix == '.dat':
        load_file_dat(file_path, type)
    else:
        pass
        #print('problema')

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def load_file_csv (file_path, type):
    print('csv')
    file_values = []
    file_values_manipulated = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            if len(row) > 0:
                if isfloat(row[0]):
                    file_values.append([float(row[0]),float(row[1])])
                    #if float(row[0]) < 600:
                    #    file_values_manipulated.append([float(row[0]), float(row[1])])
                    #else:
                    #    file_values_manipulated.append([float(row[0]), float(row[1]) + 0.01 ])
       # with open('testjump.dat', 'w') as f:
        #    for s in file_values_manipulated:
        #        f.write(f"{s[0]}" + f" {s[1]}" + '\n')

    if type == "ref_spectrum":
        current_reference_spectrum.referencespectra_measurements = file_values
    if type == "measured_spectrum":
        session_cache.original_data = file_values




def load_file_dat (file_path, type):
    file_values = []
    file = open(file_path, "r")
    for line in file:
        if isfloat(line.split()[0]):
            tmp_value = float(line.split()[1])
            if tmp_value < 0 and delete_negatives:
                tmp_value = 0
                global delete_negatives_count
                delete_negatives_count = delete_negatives_count + 1
            file_values.append([float(line.split()[0]), tmp_value])
    file.close()
    if type == "ref_spectrum":
        current_reference_spectrum.referencespectra_measurements = file_values
    if type == "measured_spectrum":
        session_cache.original_data = file_values

def load_ref_spectra_list():
    open_file = open('reference_spectra/sys/reference_spectra_list.dat', "rb")
    try:
        loaded_obj = pickle.load(open_file)
    except:
        loaded_obj = []
    open_file.close()
    return loaded_obj

def save_to_ref_spectra_list():
    open_file = open('reference_spectra/sys/reference_spectra_list.dat', "rb")
    tmp_obj = copy.deepcopy(current_reference_spectrum)

    try:
        loaded_obj = pickle.load(open_file)
        file_data = loaded_obj
    except :
        file_data = []
    open_file.close()

    tmp_obj.saved = True

    tmp_obj.id = getId(file_data)
    file_data.append(tmp_obj)

    file = open('reference_spectra/sys/reference_spectra_list.dat', "wb")
    pickle.dump(file_data, file)
    file.close()
    #print('saved')

def save_ref_spectra_list(list):

    file_data = list
    file = open('reference_spectra/sys/reference_spectra_list.dat', "wb")
    pickle.dump(file_data, file)
    file.close()

def delete_ref_spectra_list(id):
    #print(id)
    loaded_list = load_ref_spectra_list()
    i = 0
    for element in loaded_list:
        if element.id == id:
            print(id)
            print(i)
            del loaded_list[i]
        i += 1
    save_ref_spectra_list(loaded_list)

def getId(loaded_obj):
    id_list = []
    id = None
    print(id_list)
    for element in loaded_obj:
        id_list.append(element.id)
    i = 1
    print(id_list)
    max_id = 10000
    while i < max_id:
        if i in id_list:
            i += 1
        else:
            id = i
            i = max_id + 1
        print(i)
    print(id)
    return id

def saveSessionCache():
    now = datetime.now()
    dt_string = now.strftime("%d,%m,%Y_%H,%M,%S")
    session_cache.save_date = dt_string
    filename = f"saves/{session_cache.name}_" + dt_string + ".dat"
    session_cache.filename = filename
    tmp_obj = copy.deepcopy(session_cache)
    with open(filename, 'wb') as outp:
        pickle.dump(tmp_obj, outp, pickle.HIGHEST_PROTOCOL)

def loadSessionCache(filename):
    with open(filename, 'rb') as object_file:
        object = pickle.load(object_file)
    session_cache.__dict__.update(object.__dict__)



