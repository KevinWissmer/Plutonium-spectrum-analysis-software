from scipy.interpolate import CubicSpline
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
from open_save import load_file
from session_cache import session_cache
import heapq
plt.style.use('seaborn-poster')



#filepath = filedialog.askopenfilename(initialdir="./reference_spectra", title="Select a File")
#load_file(filepath, "measured_spectrum")
#print(session_cache.original_data)

x = []
y = []
old_x = 1000

def sortAndUniq(input):
  output = []
  new_x_values = []
  for element in input:
    if element[0] not in new_x_values:
        new_x_values.append(element[0])
        output.append(element)

  output.sort(key=lambda tup: tup[0])
  return output

for element in y:
    if element > 10:
        i = y.index(element)
        x.pop(i)
        y.pop(i)

#y_old = [0,1,3,7,14,31,18,11,3,0]
#x_old = [0,1,2,3,4,5,6,7,8,9]

y = [0,1,3,7,3,0]
x = [0,1,2,3,8,9]
old_x = 1000





#data = [[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[0,0],[0,0],[0,0],[0,0],]

#list = sortAndUniq(session_cache.original_data)

#for element in list:
      #x.append(element[0])
      #y.append(element[1])

#f = CubicSpline(x, y, bc_type='natural')



#x_new = np.linspace(min(x), max(x), 10000)
#y_new = f(x_new)


#with open('testjump.dat', 'w') as f:
            #for s in file_values_manipulated:
                #f.write(f"{s[0]}" + f" {s[1]}" + '\n')

from session_cache import session_cache
from open_save import load_file
import ntpath


import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve


filepath = filedialog.askopenfilename(initialdir="./reference_spectra/analysespektren", title="Select a File")
if not filepath:
    pass
else:
    session_cache.reset()
head, tail = ntpath.split(filepath)
session_cache.filename = tail
load_file(filepath, "measured_spectrum")



x_new = []
y_new = []
file_values = []
#file = open('testjump.csv', "r")


from scipy.spatial import ConvexHull
from scipy.interpolate import CubicSpline
from BaselineRemoval import BaselineRemoval

def sortAndUniq(input):
    output = []
    new_x_values = []
    for element in input:
        if element[0] not in new_x_values:
            new_x_values.append(element[0])
            output.append(element)

    output.sort(key=lambda tup: tup[0])
    return output
#print(rubberband(12,1))


def baseline_als_optimized(y, lam, p, niter=10):
    L = len(y)
    D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2))
    D = lam * D.dot(D.transpose()) # Precompute this term since it does not depend on `w`
    w = np.ones(L)
    W = sparse.spdiags(w, 0, L, L)
    for i in range(niter):
        W.setdiag(w) # Do not create a new matrix, just update diagonal values
        Z = W + D
        z = spsolve(Z, w*y)
        w = p * (y > z) + (1-p) * (y < z)
    return z

session_cache.original_data = sortAndUniq(session_cache.original_data)

f = CubicSpline([x[0] for x in session_cache.original_data],[x[1] for x in session_cache.original_data], bc_type='natural')
x_value = []
y_value = []
#print(max([x[0] for x in session_cache.original_data]))
for x in range(0,450):
    y_value.append(f(400+x))
    x_value.append(400 + x)
y_value = baseline_als_optimized(y_value)

y_value_new = []
x_value_new = []
f = CubicSpline(x_value,y_value, bc_type='natural')
for element in session_cache.original_data:
    y_value_new.append(f(element[0]))
    x_value_new.append(element[0])

plt.figure(figsize = (10,8))

j=0
tmp_y_new = []
for element in y_value_new:
    tmp_y_new.append(session_cache.original_data[j][1] - element)
    j += 1
y_value_new = tmp_y_new

plt.plot(x_value,y_value, color="black")
#plt.plot(x_value,Zhangfit_output, color="green")
plt.plot([x[0] for x in session_cache.original_data],[x[1] for x in session_cache.original_data], color="blue")
plt.plot(x_value,y_value, color="red")
#plt.plot([400,850],[0,0], color="black")
plt.plot(x_value_new, y_value_new, color="green", linestyle="--")
#plt.scatter(x,y,s=20, color="blue")
plt.title('Cubic Spline Interpolation')
plt.xlabel('x')
plt.ylabel('y')
plt.show()

baseline_als_optimized(y_value,100000,0.00001)



#fig, [[ax1,ax2,ax3,ax4,ax5],[ax11,ax12,ax13,ax14,ax15],[ax21,ax22,ax23,ax24,ax25],[ax31,ax32,ax33,ax34,ax35],[ax41,ax42,ax43,ax44,ax45]] = plt.subplots(5, 5)
#print(fig.get_axes())
#fig, [[ax1,ax2,ax3],[ax11,ax12,ax13],[ax21,ax22,ax23]] = plt.subplots(3, 3)
p = 0
'''
for ax_list in [[ax1,ax2,ax3,ax4,ax5],[ax11,ax12,ax13,ax14,ax15],[ax21,ax22,ax23,ax24,ax25],[ax31,ax32,ax33,ax34,ax35],[ax41,ax42,ax43,ax44,ax45]] :
    lam = 0
    for ax in ax_list:
        ax.plot([x[0] for x in session_cache.original_data],[x[1] for x in session_cache.original_data], color="black")
        ax.plot(x_value, baseline_als_optimized(y_value, 0.00001 * 100**lam, 0.00001 * 100**p), 'tab:red')
        ax.set_title(f"lam = {'{:.1e}'.format(0.00001 * 100**lam)},p = {'{:.1e}'.format(0.00001 * 100**p)}")
        ax.axis('off')
        lam += 1
    p += 1
'''
'''
for ax_list in [[ax1,ax2,ax3],[ax11,ax12,ax13],[ax21,ax22,ax23]] :
    lam = 0
    for ax in ax_list:
        ax.plot([x[0] for x in session_cache.original_data],[x[1] for x in session_cache.original_data], color="black")
        ax.plot(x_value, baseline_als_optimized(y_value, 100 * 10**lam, 0.000001 * 10**p), 'tab:red')
        ax.set_title(f"Nr.{lam+(p*3)}    lam = {'{:.1e}'.format(10 * 10**lam)},p = {'{:.1e}'.format(0.000001 * 10**p)}")
        ax.axis('off')
        lam += 1
    p += 1
'''


'''
fig.suptitle('Sharing x per column, y per row')
ax1.plot(x_value, baseline_als_optimized(y_value,0.001,0.00001), 'tab:red')
ax2.plot(x_value, baseline_als_optimized(y_value,0.001,0.1), 'tab:red')
ax3.plot(x_value, baseline_als_optimized(y_value,0.001,100), 'tab:red')

#2.reihe
ax4.plot(x_value,  baseline_als_optimized(y_value,100,0.00001), 'tab:red')
ax5.plot(x_value, baseline_als_optimized(y_value,1000,0.1), 'tab:red')
ax6.plot(x_value, baseline_als_optimized(y_value,1000,100), 'tab:red')

#3.reihe
ax7.plot(x_value, baseline_als_optimized(y_value,100000,0.00001), 'tab:red')
ax8.plot(x_value,  baseline_als_optimized(y_value,100000,0.1), 'tab:red')
ax9.plot(x_value, baseline_als_optimized(y_value,100000,100), 'tab:red')
'''

#ax1.set_title("0.001,0.00001")
plt.show()


'''
for line in file:
    y_new.append(float(line.split()[1]))
    x_new.append(float(line.split()[0]))
    file_values.append([x_new, y_new])

file.close()
'''

'''
y_old = 0
x_old = 0
i = 0
steigung_max = 0
steigung_max_2 = 0
steigungen = []
sprünge = []
for element in x_new:
    if i >= 3:
        #print(element[1])
        steigung1 = abs(y_new[i - 2] - y_new[i-3])# / (x_new[i - 2] - x_new[i-3])
        steigung2 = abs(y_new[i - 1] - y_new[i - 2])# / (x_new[i - 1] - x_new[i - 2])
        steigung3 = abs(y_new[i] - y_new[i - 1])# / (x_new[i] - x_new[i - 1])
        steigungen.append(steigung1)
        #print((steigung1 + steigung2) * 2)
        #print(steigung3)
        if steigung3 / (steigung1 + steigung2) > 10:
            print(x_new[i])
            sprünge.append([i,[],[]])


    i += 1

#print(steigung_max)
#print(heapq.nlargest(5, steigungen))

for element in sprünge:
    distance = abs(y_new[element[0]] - y_new[element[0] - 1])
    i=0
    for element2 in x_new:
        print(distance)
        y_value = y_new[i]
        if element2 > x_new[element[0]]:
            y_value = y_value - distance
        element[1].append(element2)
        element[2].append(y_value)
        i +=1

'''




















'''

        def cubicSpline(self, x_new, i):
        x = []
        y = []
        for element in self.referencespectra_list[i]:
            x.append(element[0])
            y.append(element[1])

        x = self.sortAndUniq(x)
        f = CubicSpline(x, y, bc_type='natural')
        return f(x_new)
    
    
    
    
    
    
    
    
    
    
    
    def createSingleFitParamManipulationElementLabelSingle(self,i):
        label = ttk.Label(self.fit_param_manipulation_frame, text=self.fit_param_vars_values_list[i][0].get())
        label.grid(column=2, row=i * 10, padx=5, pady=5, columnspan=2, rowspan=2)

        self.button_edit_1 = ttk.Button(self.fit_param_manipulation_frame, text="edit", command=lambda: self.updateFitParamManipulation('single_edit',i) )
        self.button_edit_1.grid(column=8, row=i * 10, padx=20, pady=0, columnspan=1, rowspan=2)
        self.button_switch_1 = ttk.Button(self.fit_param_manipulation_frame, text="switch", command=lambda: self.updateFitParamManipulation('double_non_edit',i))
        self.button_switch_1.grid(column=10, row=i * 10, padx=0, pady=0, columnspan=1, rowspan=2)

    def createSingleFitParamManipulationElementEntrySingle(self,i):
        element = tk.Entry(self.fit_param_manipulation_frame, textvariable= self.fit_param_vars_values_list[i][0],width=10)
        element.grid(column=3, row=i * 10, padx=5, pady=5, columnspan=2, rowspan=2)

        self.button_edit_1 = ttk.Button(self.fit_param_manipulation_frame, text="save", command=lambda: self.updateFitParamManipulation('single_non_edit',i) )
        self.button_edit_1.grid(column=8, row=i * 10, padx=20, pady=0, columnspan=1, rowspan=2)
        self.button_switch_1 = ttk.Button(self.fit_param_manipulation_frame, text="switch", command=lambda: self.updateFitParamManipulation('double_edit',i))
        self.button_switch_1.grid(column=10, row=i * 10, padx=0, pady=0, columnspan=1, rowspan=2)

    def createSingleFitParamManipulationElementEntryArea(self, i):
        element = tk.Entry(self.fit_param_manipulation_frame, textvariable=self.fit_param_vars_values_list[i][0],width=10)
        element.grid(column=3, row=i * 10, padx=5, pady=5, columnspan=2, rowspan=2)
        label_middle = ttk.Label(self.fit_param_manipulation_frame, text=f"-")
        label_middle.grid(column=4, row=i * 10, padx=5, pady=5, columnspan=2, rowspan=2)
        element = tk.Entry(self.fit_param_manipulation_frame, textvariable=self.fit_param_vars_values_list[i][1],width=10)
        element.grid(column=6, row=i * 10, padx=5, pady=5, columnspan=2, rowspan=2)

        self.button_edit_1 = ttk.Button(self.fit_param_manipulation_frame, text="save", command=lambda: self.updateFitParamManipulation('double_non_edit',i))
        self.button_edit_1.grid(column=8, row=i * 10, padx=20, pady=0, columnspan=1, rowspan=2)
        self.button_switch_1 = ttk.Button(self.fit_param_manipulation_frame, text="switch", command=lambda: self.updateFitParamManipulation('single_edit',i))
        self.button_switch_1.grid(column=10, row=i * 10, padx=0, pady=0, columnspan=1, rowspan=2)

    def createSingleFitParamManipulationElementLabelArea(self, i):
        label_left = ttk.Label(self.fit_param_manipulation_frame, text=self.fit_param_vars_values_list[i][0].get())
        label_left.grid(column=2, row=i * 10, padx=5, pady=5, columnspan=2, rowspan=2)
        label_middle = ttk.Label(self.fit_param_manipulation_frame, text=f"-")
        label_middle.grid(column=4, row=i * 10, padx=5, pady=5, columnspan=2, rowspan=2)
        label_right = ttk.Label(self.fit_param_manipulation_frame, bg="grey", text=self.fit_param_vars_values_list[i][1].get())
        label_right.grid(column=6, row=i * 10, padx=5, pady=5, columnspan=2, rowspan=2)

        self.button_edit_1 = ttk.Button(self.fit_param_manipulation_frame, text="edit", command=lambda: self.updateFitParamManipulation('double_edit',i))
        self.button_edit_1.grid(column=8, row=i * 10, padx=20, pady=0, columnspan=1, rowspan=2)
        self.button_switch_1 = ttk.Button(self.fit_param_manipulation_frame, text="switch", command=lambda: self.updateFitParamManipulation('single_non_edit',i))
        self.button_switch_1.grid(column=10, row=i * 10, padx=0, pady=0, columnspan=1, rowspan=2)


ttk.Frame.__init__(self, parent)
self.parent = parent

self.specs_list = []
self.specs_labelname_list = ['Name', 'Cuvettesize', 'Norm.-factor', 'Solution']

self.current_fit_status = 'none'
self.specs_manipulation_status = "non_edit"
self.fit_specs_vars_values_list = []
self.specs_manipulation_frame = tk.Frame(self, height=120, background=design_scheme.bg_color,
                                         highlightbackground=design_scheme.border_color,
                                         highlightthickness=design_scheme.h_thickness, bd=0)
self.specs_manipulation_frame.pack(expand=1, fill="x", padx=10, pady=10, side='top')
self.specs_manipulation_frame.propagate(1)
self.initSpecsVariables()
self.specs_manipulation = self.specsManipulationWidget()

self.lower_tab_frame = tk.Frame(self, height=320, background=design_scheme.bg_color,
                                highlightbackground=design_scheme.border_color,
                                highlightthickness=design_scheme.h_thickness, bd=0)
self.lower_tab_frame.pack(expand=1, fill="both", padx=10, pady=10, side='right')
self.lower_tab_frame.propagate(0)

self.manipulation_label_names = ["Fit area", "omitted area 1", "omitted area 2", "omitted area 3"]
self.fit_manipulation_checkbox_consider_vars_list = []
self.fit_manipulation_checkbox_show_vars_list = []
self.fit_manipulation_vars_values_list = [[], [], [], []]
self.fit_manipulation_status_list = [["non_edit", "non_edit"], ["non_edit", "non_edit"], ["non_edit", "non_edit"],
                                     ["non_edit", "non_edit"]]


self.fit_manipulation_frame.propagate(0)
self.initManipulationVariables()
self.fit_manipulation = self.fitManipulationWidget()

self.fit_param_label_names = ["PUIII", "PUIV", "PUV", "PUVI", "Colloid"]
self.fit_param_type_label_names = ["Start", "Minimum", "Maximum"]
self.fit_param_manipulation_status_list = ["non_edit", "non_edit", "non_edit", "non_edit", "non_edit"]
self.fit_param_manipulation_frame = tk.Frame(self.lower_tab_frame, background=design_scheme.bg_color,
                                             highlightbackground=design_scheme.border_color,
                                             highlightthickness=design_scheme.h_thickness, bd=0)
self.fit_param_manipulation_frame.pack(expand=1, fill="both", padx=10, pady=10, side='left')
self.fit_param_manipulation_frame.propagate(0)
self.fit_param_vars_values_list = []
self.initParamVariables()
self.fit_param_manipulation = self.fitParamManipulationWidget("non_edit")

'''





















