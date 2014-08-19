
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
from matplotlib.patches import Ellipse

sns.set_style("whitegrid")
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
    svg=None
    def __init__(self,main_group_df):
        grouped_group = main_group_df.groupby('status')
        group_df = grouped_group.get_group('active')

        self.xpoints = group_df["concentration"].tolist()
        self.ypoints = group_df["percent_inhib"].tolist()
        self.x = np.array(self.xpoints)
        self.data = np.array(self.ypoints)
        self.labels = group_df["full_ref"].tolist()
        self.inactivex = []
        self.inactivey = []
        self.inactivelabels = []
        if "inactive" in grouped_group.groups:
            inactive = grouped_group.get_group('inactive')
            self.inactivex = inactive["concentration"].tolist()
            self.inactivey = inactive["percent_inhib"].tolist()
            self.inactivelabels = inactive["full_ref"].tolist()




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
        self.results = result.values
        self.results["logIC50error"] = result.params["logIC50"].stderr
        self.results["hillerror"] = result.params["hill"].stderr
        #Calculate an average % error across the hill and IC50 if greater than 30% we can scrap the result
        self.results["errorpercent"] = 50 * ((float(self.results["logIC50error"]) / float(self.results["logIC50"])) +
                                                (float(self.results["hillerror"]) / float(self.results["hill"])))
        self.results["max"] = max(self.data)
        self.results["min"] = min(self.data)
        self.results["message"] = ""
        if self.results["max"] < 80:
            self.results["message"] = "Low total inhibition, values could be inaccurate"
        if self.results["min"] > 20:
            self.results["message"] = "No low inhibition range - values could be inaccurate"
        if self.results["errorpercent"] > 20 or self.results["errorpercent"] < -20:
            self.results["message"] = "Error, no good line fit found"

        xnew = np.linspace(self.x.min(),self.x.max(),300)
        ynew = [(result.values["bottom"] + (result.values["top"] - result.values["bottom"])/(1 + np.exp((result.values["logIC50"] - xdatum)*result.values["hill"]))) for xdatum in xnew]
   
        smooted_best_fit_line = spline(xnew,ynew,xnew)
        f = figure(figsize=(6,4))
        #plt.plot(self.x, self.data, 'o', )
        plt.plot(self.inactivex, self.inactivey, 'o', color='0.75' )
        plt.xlim(0,max(self.x)*1.1)
        plt.ylim(-10,110)
        plt.plot(xnew,smooted_best_fit_line, 'b')
        el = Ellipse((2, -1), 0.5, 0.5)
        stuff = 8
        


        for  label, x, y in zip(self.labels, self.x, self.data):

            plt.annotate(
            "%s" % label , 
            xy = (x, y), 
            gid="%d" % (x + y),
            url = "/blarrrr",
            size=8,
            xytext=(stuff, -1*stuff), 
            textcoords='offset points',
            va="center",
            bbox=dict(boxstyle="round", 
            fc=(1.0, 0.7, 0.7), 
            ec="none"),
            arrowprops=dict(arrowstyle="wedge,tail_width=1.",
                                fc=(1.0, 0.7, 0.7), ec="none",
                                patchA=None,
                                patchB=el,
                                relpos=(0.2, 0.5),
                                )
                )
            if stuff == 8:
                stuff = -12
            else:
                stuff = 8
        self.svg = get_svg(f)
        plt.close(f)
        


def get_svg(fig):
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    return imgdata.buf