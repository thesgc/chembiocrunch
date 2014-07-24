from django.shortcuts import render, redirect
from django.views.generic import View,  DetailView, ListView, CreateView
from django.views.generic.detail import SingleObjectMixin

from braces.views import LoginRequiredMixin

from django.db.models import get_model

from workflows import WorkflowDetailView
from django.http import HttpResponseRedirect

import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib as mpl
import matplotlib.pyplot as plt
from workflow.forms import PlotForm
# '''
# cluster
# http://altanalyze.blogspot.co.uk/2012/06/hierarchical-clustering-heatmaps-in.html
# '''

class VisualisationView(WorkflowDetailView):
    template_name = "visualise/visualise.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VisualisationView, self).get_context_data(**kwargs)
        if not "form" in kwargs:
            form = PlotForm()
        else:
            form= kwargs.get("form")
        context["form"] = form
        return context
