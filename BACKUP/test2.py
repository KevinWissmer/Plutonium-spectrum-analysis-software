from BaselineRemoval import BaselineRemoval

input_array=[10,20,1.5,5,2,9,99,25,47]

polynomial_degree=1 #only needed for Modpoly and IModPoly algorithm

baseObj=BaselineRemoval(input_array)

Modpoly_output=baseObj.ModPoly(polynomial_degree)

Imodpoly_output=baseObj.IModPoly(polynomial_degree)

Zhangfit_output=baseObj.ZhangFit()

print('Original input:',input_array)

print('Modpoly base corrected values:',Modpoly_output)

print('IModPoly base corrected values:',Imodpoly_output)

print('ZhangFit base corrected values:',Zhangfit_output)

