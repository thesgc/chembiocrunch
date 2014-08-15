
# coding: utf-8

# In[1]:
from StringIO import StringIO
from lmfit import minimize, Parameters, Parameter, report_fit
import numpy as np

from scipy.interpolate import spline
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib.figure as mfigure
from matplotlib.backends.backend_agg import FigureCanvasAgg #canvas
from pylab import figure, axes, pie, title

def ic50min(params, x, data):
    """ model ic50 data"""
    bottom = params['bottom'].value
    top = params['top'].value
    logIC50 = params['logIC50'].value
    hill = params['hill'].value
    model =  (bottom + (top - bottom)/(1 + np.exp((logIC50 - x)*hill)))
    return model - data


class IC50CurveFit(object):
    xpoints = []
    ypoints = []
    result = None

    def __init__(self,xpoints, ypoints):
        self.xpoints = xpoints.tolist()
        self.ypoints = ypoints.tolist()
        self.x = np.array(xpoints)
        self.data = np.array(ypoints)

    def get_fit(self, constrained=None):
        # do fit, here with leastsq model
        vary = True
        if constrained:
            vary = False
        params = Parameters()
        params.add('bottom',   value= 0, vary=vary)
        params.add('top', value=100, vary=False)
        params.add('logIC50', value= 1)
        params.add('hill', value= 2)
        result = minimize(ic50min, params, args=( self.x, self.data))

        report_fit(params)
        xnew = np.linspace(self.x.min(),self.x.max(),300)
        ynew = [(result.values["bottom"] + (result.values["top"] - result.values["bottom"])/(1 + np.exp((result.values["logIC50"] - xdatum)*result.values["hill"]))) for xdatum in xnew]
   
        smooted_best_fit_line = spline(xnew,ynew,xnew)
        f = figure(figsize=(6,6))
        plt.plot(self.x, self.data, 'k+')
        plt.plot(xnew,smooted_best_fit_line, 'b')
        svg = get_svg(f)
        plt.close(f)
        return svg


def get_svg(fig):
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    return imgdata.buf