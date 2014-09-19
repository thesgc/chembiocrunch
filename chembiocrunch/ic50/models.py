from django.db import models
from django.db import models
from pandas.io.pytables import get_store
from django_extensions.db.models import TimeStampedModel
from pandas import DataFrame, read_hdf
from django.db.models import get_model
from django.template.defaultfilters import slugify
import json
from django.conf import settings
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from StringIO import StringIO

from seaborn import plotting_context, set_context
import mpld3
from workflow.basic_units import BasicUnit
from cbc_common.dataframe_handler import get_config_columns, zero_pad_object_id

from workflow.models import Visualisation, my_slug
from multiprocessing import Lock, Process, Queue, current_process
from datetime import datetime
from ic50.curve_fit import IC50CurveFit
from pandas.io.json import read_json
# Create your models here.
UPLOAD ="up"
VALIDATE_COLUMNS ="vc"

REVISION_TYPES = (
    (UPLOAD, "Upload"),
    (VALIDATE_COLUMNS, "Validate Columns")
)
# PB - new Workflow for IC50 project.
from cbc_common import dataframe_handler


class IC50WorkflowManager(models.Manager):
    def get_user_records(self, user):
        return self.filter(created_by__groups__name__in=["affiliation:sgc","affiliation:tdi",] archived=False)

    def get_latest_workflow_revision(self, workflow_id):
        return get_model("ic50", "IC50WorkflowRevision").objects.filter(workflow_id=workflow_id, archived=False).order_by("created")[0]



class IC50Workflow(TimeStampedModel):
    '''Object to hold the data files for a specific IC50 workflow'''
    title = models.CharField(max_length=300,)
    uploaded_config_file = models.FileField(max_length=1024)
    uploaded_data_file = models.FileField(max_length=1024)
    uploaded_meta_file = models.FileField(max_length=1024)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey('auth.User')
    workflow_type = "ic50workflow"

    objects = IC50WorkflowManager()

    #def get_latest_data_revision(self):
    #    return get_model("workflow", "Ic50Workflow").objects.get_latest_workflow_revision(self.id)


    def get_upload_to(self, name):
        return "%s/ic50workflows/%d/%s" % (settings.MEDIA_ROOT, 
            self.id, 
            name)

    def get_latest_workflow_revision(self):
        return get_model("ic50", "IC50WorkflowRevision").objects.filter(workflow_id=self.id).order_by("pk")[0]


class IC50WorkflowRevision(TimeStampedModel):

    '''
    Name is historical - this object holds reference to a specific plate in the 
    assay data results including reference to the dataset for that plate
    the datasets are split out into separate dataframes at the point of
    saving the intial data files (the IC50 workflow)
    '''

    workflow = models.ForeignKey('IC50Workflow', related_name='workflow_ic50_revisions')
    plate_name = models.CharField(max_length=30, default="")
    steps_json = models.TextField(default="[]")

    @property
    def previous(self):
        '''Get the previous item belongin to this workflow'''
        qs = self.workflow.workflow_ic50_revisions.filter(pk__lt=self.id).order_by("-pk")
        if qs.count() == 0:
            return None
        else:
            return qs[0]

    @property
    def next(self):
        '''Get the next item belonging to this workflow'''
        qs = self.workflow.workflow_ic50_revisions.filter(pk__gt=self.id).order_by("pk")
        if qs.count() == 0:
            return None
        else:
            return qs[0]



    def get_store(self):
        return get_store('workflows.%s' % (zero_pad_object_id(self.id),))


    def get_store_filename(self,dtype ):
        return '%sic50_workflows%s.%s.%s' % (settings.HDF5_ROOT, dtype, zero_pad_object_id(self.workflow_id),  zero_pad_object_id(self.id))

    def get_store_key(self):
        return "ic50_wfdr_%s" % (  zero_pad_object_id(self.id),)


    def get_data(self):
        '''one dataset per workflow revision'''
        filename=self.get_store_filename("data")
        df = read_hdf(filename,self.get_store_key(),)
        return df

    def get_config_data(self):
        filename=self.get_store_filename("configdata")
        return read_hdf(filename,self.get_store_key(),)

    def get_meta_data(self):
        filename=self.get_store_filename("metadata")
        return read_hdf(filename,self.get_store_key(),)


class IC50VisualisationManager(models.Manager):
    '''Retrieves visible lists of workflows using the revision id'''
    def by_workflow(self, workflow):
        return self.filter(data_mapping_revision__workflow_id=workflow.id).order_by("-created")

    def by_workflow_revision(self, workflow_revision):
        return self.filter(data_mapping_revision_id=workflow_revision.id).order_by("-created")






class IC50Visualisation(TimeStampedModel):
    '''
    Holder object for an IC50 visualisation - there will be a set of these for each
    IC50 workflow revision
    '''
    data_mapping_revision = models.ForeignKey('IC50WorkflowRevision', related_name="visualisations")
    x_axis = models.CharField(max_length=200, default="Destination Concentration")
    y_axis = models.CharField(max_length=200, default='Percent inhibition')
    compound_id = models.CharField(max_length=200)
    error_bars = models.NullBooleanField()
    results = models.TextField(default="{}")
    visualisation_title = models.CharField(max_length=200, null=True, blank=True) #Will be used for the sample name
    config_json = models.TextField(default="{}")
    html = models.TextField(default="")
    png = models.FileField(blank=True,null=True, default=None )
    thumb = models.FileField(blank=True, null=True, default=None)
    constrained = models.NullBooleanField()
    objects = IC50VisualisationManager()
    raw_data = models.TextField(default="{}")
    marked_as_bad_fit = models.BooleanField(default=False)



    def get_upload_to(self, name):
        return "%s/plates/%d/compounds/%s/%s" % (settings.MEDIA_ROOT, 
            self.data_mapping_revision_id, 
            self.compound_id, 
            name)

    def get_curve_fitter(self):

        group_df = read_json(self.raw_data)

        group_df.sort(["percent_inhib","concentration"], inplace=True)
        curve_fitter = IC50CurveFit(main_group_df=group_df)
        curve_fitter.get_fit(constrained=True)
        return curve_fitter


    def get_svg(self):
        imgdata = StringIO()
        fig = self.get_fig_for_dataframe()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)
        return imgdata.buf


    def error_class(self):
        #get the results
        #find the error message part
        #output the appropriate css class for each error
        results = json.loads(self.results)
        error_msg = results['values']['message']
        print error_msg
        if self.marked_as_bad_fit:
            return 'ic50-error-4'
        elif error_msg == "Low total inhibition, values could be inaccurate":
            return 'ic50-error-1'
        elif error_msg == "No low inhibition range - values could be inaccurate":
            return 'ic50-error-2'
        elif error_msg == "Error, no good line fit found":
            return 'ic50-error-3'
        else:
            return ''        




