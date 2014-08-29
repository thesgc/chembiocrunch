
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
    """ model for ic50 curves - this function contains the equation used for fitting the data"""
    bottom = params['bottom'].value
    top = params['top'].value
    logIC50 = params['logIC50'].value
    hill = params['hill'].value
    model =  (bottom + (top - bottom)/(1 + np.exp((logIC50 - x)*hill)))
    return model - data


class IC50CurveFit(object):
    '''Holder class for IC50 plotting functions
    Can be initialised with either a dataframe for that section of the data or with a
    results dictionary which contains ready-processed data '''
    xpoints = []
    ypoints = []
    result = None
    svg=None
    def __init__(self,*args, **kwargs):
        
        if "main_group_df"  in kwargs:
            main_group_df = kwargs.get("main_group_df", "None")
            grouped_group = main_group_df.groupby('status')
            group_df = grouped_group.get_group('active')

            self.xpoints = group_df["concentration"].tolist()
            self.ypoints = group_df["percent_inhib"].tolist()
           
            self.labels = group_df["full_ref"].tolist()
            self.inactivex = []
            self.inactivey = []
            self.inactivelabels = []
            self.xcurve = None
            self.ycurve = None
            self.fig = None
            if "inactive" in grouped_group.groups:
                inactive = grouped_group.get_group('inactive')
                self.inactivex = inactive["concentration"].tolist()
                self.inactivey = inactive["percent_inhib"].tolist()
                self.inactivelabels = inactive["full_ref"].tolist()
        results = kwargs.get("results", None)
        if results:
            self.results = results
            self.inactivex = self.results["inactivex"] 
            self.labels = self.results["labels"]
            self.inactivey = self.results["inactivey"]
            self.xpoints = self.results["xpoints"]
            self.ypoints = self.results["ypoints"]
        self.x = np.log10(np.array(self.xpoints))
        self.data = np.array(self.ypoints)


    def get_fit(self, constrained=None):
        '''This fuction runs the curve fitting using the lmfit module
        - assumes that the class has been initialised with 
        a dataframe'''
        vary = True
        if constrained:
            vary = False
        params = Parameters()
        params.add('bottom',   value= 0, vary=vary)
        params.add('top', value=100, vary=vary)
        params.add('logIC50', value= 1)
        params.add('hill', value= 2)
        result = minimize(ic50min, params, args=( self.x, self.data))
        self.results = result.values
        self.results["xpoints"] = self.xpoints
        self.results["ypoints"] = self.ypoints
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
        self.results["inactivex"] = self.inactivex
        self.results["labels"] = self.labels
        self.results["inactivey"] = self.inactivey




    def get_fig(self, labels=True):
        xcurve = np.linspace(self.x.min(),self.x.max(),300)
        ycurve = [(self.results["bottom"] + (self.results["top"] - self.results["bottom"])/(1 + np.exp((self.results["logIC50"] - xdatum)*self.results["hill"]))) for xdatum in xcurve]
        smooted_best_fit_line = spline(xcurve,ycurve,xcurve)
        xmin = min(self.x)
        if xmin > 0 :
            xmin = 0
        else:
            xmin = xmin * 1.1
        f = figure(figsize=(6,4))
        plt.plot(self.inactivex, self.inactivey, "D", color='0.55' )
        plt.plot(self.x, self.data, 'o', )
        plt.xlim(xmin,max(self.x)*1.1)
        plt.ylim(-10,110)
        plt.plot(xcurve,smooted_best_fit_line, 'b')
        self.fig = f
        plt.xlabel(u'Log (micromolar concentration)')
        plt.ylabel(u'% Inhibition')
        f.tight_layout()

        if labels:
            self.add_labels()
            self.add_labels(inactivelabels=True)    
        self.svg = get_svg(f)
        plt.close(f)


        

    def add_labels(self, inactivelabels=False):
        '''Add labels to the graph for the points to show the well code, including
        grey labels if we are labelling inactive data'''
        el = Ellipse((2, -1), 0.5, 0.5)
        stuff = 8
        if not inactivelabels:
            labeldata = zip(self.labels, self.x, self.data)
            fc = (1.0, 0.7, 0.7)
        else:
            labeldata = zip(self.inactivelabels, self.inactivex, self.inactivey, )
            fc = "0.55"
        for  label, x, y in labeldata:

            plt.annotate(
            "%s" % label ,
            xy = (x, y),
            gid="point_label_%s" % label,
            size=8,
            xytext=(stuff, -1*stuff),
            textcoords='offset points',
            va="center",
            bbox=dict(boxstyle="round",
            fc=fc,
            ec="none"),
            arrowprops=dict(arrowstyle="wedge,tail_width=1.",
                                fc=fc, ec="none",
                                patchA=None,
                                patchB=el,
                                relpos=(0.2, 0.5),
                                )
                )
            if stuff == 8:
                stuff = -12
            else:
                stuff = 8



def get_svg(fig):
    '''Return an svg for a matplotlib fig'''
    imgdata = StringIO()
    fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    return imgdata.buf
