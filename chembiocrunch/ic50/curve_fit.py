
# coding: utf-8

# In[1]:

from lmfit import minimize, Parameters, Parameter, report_fit
import numpy as np


# In[2]:

import pylab


# In[94]:

get_ipython().magic(u'matplotlib inline')
graphpoints = np.linspace(0, 20, 500)
# data = (5. * np.sin(2 * x - 0.1) * np.exp(-x*x*0.025) +
#         np.random.normal(size=len(x), scale=0.2) )
ypoints = [94.7275343205,99.8681134225,98.0306936035,88.6457646424,89.3201846412,96.0164258737,89.5150170853,80.5257478568,62.4033331335,82.9146933637,64.0279359751,64.5255080631,14.9031832624,16.2790000599,1.3278580421,1.4387626641,0.1228943109,0.1498711108,0.1228943109,0.0839278221,0.1528685331,3.3391283496,0.2817576884,]
xpoints = [0.02,0.02,0.03906,0.03906,0.07813,0.07813,0.1563,0.1563,0.3125,0.3125,0.625,0.625,1.25,1.25,2.5,2.5,5,5,10,10,10,20,20,]
x = np.array(xpoints)
data = np.array([100-ypoint for ypoint in ypoints])
import pylab
from scipy.interpolate import spline

def ic50min(params, x, data):
    """ model ic50 data"""
    
    
    bottom = params['bottom'].value
    top = params['top'].value
    logIC50 = params['logIC50'].value
    hill = params['hill'].value
    model =  (bottom + (top - bottom)/(1 + np.exp((logIC50 - x)*hill)))
    return model - data

# def fcn2min(params, x, data):
#     """ model decaying sine wave, subtract data"""
#     amp = params['amp'].value
#     shift = params['shift'].value
#     omega = params['omega'].value
#     decay = params['decay'].value

#     model = amp * np.sin(x * omega + shift) * np.exp(-x*x*decay)
#     return model - data

# create a set of Parameters
params = Parameters()
params.add('bottom',   value= 0)
params.add('top', value=100)
params.add('logIC50', value= 1)
params.add('hill', value= 2)


# do fit, here with leastsq model
result = minimize(ic50min, params, args=(x, data))

# calculate final result
#final = data + result.residual

# write error report
report_fit(params)
xnew = np.linspace(x.min(),x.max(),300)
ynew = [(result.values["bottom"] + (result.values["top"] - result.values["bottom"])/(1 + np.exp((result.values["logIC50"] - xdatum)*result.values["hill"]))) for xdatum in xnew]

# try to plot results

    
smooted_best_fit_line = spline(xnew,ynew,xnew)

pylab.plot(x, data, 'k+')
pylab.plot(xnew,smooted_best_fit_line, 'b')
pylab.show()


# In[95]:

sp.sqrt(x)


# In[96]:

import scipy as sp
sp.sqrt(x)


# In[100]:

ar = np.array([1,4])
sp.sqrt(ar*ar*ar)


# In[ ]:

#http://stackoverflow.com/questions/15255928/how-do-i-include-errors-for-my-data-in-the-lmfit-least-squares-miniimization-an
