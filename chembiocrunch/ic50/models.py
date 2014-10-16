# -*- coding: utf8 -*-
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
from django.conf import  settings

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from StringIO import StringIO

from seaborn import plotting_context, set_context
import mpld3
from workflow.basic_units import BasicUnit
from cbc_common.dataframe_handler import zero_pad_object_id

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
        return self.filter( archived=False)

    def get_latest_workflow_revision(self, workflow_id):
        return get_model("ic50", "IC50WorkflowRevision").objects.filter(workflow_id=workflow_id, archived=False).order_by("created")[0]



class IC50Workflow(TimeStampedModel):
    '''Object to hold the data files for a specific IC50 workflow'''
    title = models.CharField(max_length=300,)
    uploaded_config_file = models.FileField(max_length=1024)
    uploaded_data_file = models.FileField(max_length=1024)
    uploaded_meta_file = models.FileField(max_length=1024)
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    workflow_type = "ic50workflow"

    objects = IC50WorkflowManager()
    metadata = DataFrame()
    #def get_latest_data_revision(self):
    #    return get_model("workflow", "Ic50Workflow").objects.get_latest_workflow_revision(self.id)


    def get_upload_to(self, name):
        return "%s/ic50workflows/%d/%s" % (settings.MEDIA_ROOT, 
            self.id, 
            name)

    def get_latest_workflow_revision(self):
        return get_model("ic50", "IC50WorkflowRevision").objects.filter(workflow_id=self.id).order_by("pk")[0]

    def get_meta_data(self):
        filename=self.get_store_filename("metadata")
        return read_hdf(filename,self.get_store_key(),)

    def get_store_key(self):
        return "ic50_wfdr_%s" % (  zero_pad_object_id(self.id),)

    def get_store_filename(self,dtype ):
        return '%sic50_workflow_meta%s.%s' % (settings.HDF5_ROOT, dtype, zero_pad_object_id(self.id))


    def set_meta_data(self, df):
        filename=self.get_store_filename("metadata")
        df.to_hdf(filename,self.get_store_key(),mode="w")

    def meta_by_name(self, fieldname):
        if self.metadata.empty:
            self.metadata = self.get_meta_data().replace(np.nan, "")
        dataset = self.metadata[self.metadata[4].str.lower().isin([fieldname.lower(),]) & self.metadata[5].notnull()]
        value = ""
        if not dataset.empty:
            value = dataset[5].tolist()[0]
            print value
        return value

    def get_username_for_export(self):
        if self.created_by.first_name and self.created_by.last_name:
            return "%s%s" % (self.created_by.first_name[1].upper() , self.created_by.last_name.upper())
        return self.created_by.username.upper()

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
    minimum = models.FloatField(default=0)
    minimum_error = models.FloatField(default=0)
    maximum = models.FloatField(default=0)
    maximum_error = models.FloatField(default=0)
    solvent_maximum = models.FloatField(default=0)
    solvent_maximum_error = models.FloatField(default=0)  



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
    GOOD_CURVE = "Good Curve"              
    TOP_BELOW_80 =  "Top plateaus at below 80%"               
    BOTTOM_ABOVE_20 = "Bottom plateaus above 20%"             
    TOP_ABOVE_120 = "Top plateaus above 120 %"              
    BOTTOM_BELOW_MINUS_20 = "Bottom plateaus below- 20%"              
    INCOMPLETE = "incomplete curve"      
    POOR_CURVE = "poor curve"       
    INACTIVE = "inactive compound"               
    STEEP_HILL = "steep hillslope"      
    TOP_NO_PLATEAUX = "Top of curve does not plateaux"
    COMMENT_CHOICES = ((GOOD_CURVE, GOOD_CURVE),
                        (TOP_BELOW_80, TOP_BELOW_80),
                        (BOTTOM_ABOVE_20, BOTTOM_ABOVE_20),
                        (TOP_ABOVE_120, TOP_ABOVE_120),
                        (BOTTOM_BELOW_MINUS_20, BOTTOM_BELOW_MINUS_20),
                        (INCOMPLETE, INCOMPLETE),
                        (POOR_CURVE, POOR_CURVE),
                        (INACTIVE, INACTIVE),
                        (STEEP_HILL, STEEP_HILL),
                        (TOP_NO_PLATEAUX, TOP_NO_PLATEAUX),)

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
    raw_dataframe = DataFrame()
    comment = models.CharField(max_length=30, choices=COMMENT_CHOICES, default=GOOD_CURVE)


    def get_results_for_datapoint(self):
        '''When ordered by concentration, take the nth group and do an average - only used for the 
        export to beehive function'''
        raw_dataframe = read_json(self.raw_data)
        raw_dataframe.sort(["concentration"], inplace=True)
        raw_dataframe = raw_dataframe.groupby("concentration")
        index = 0
        for index, group in enumerate(raw_dataframe.groups):
            concentration = group
            df = raw_dataframe.get_group(group)
            inhibition = df["percent_inhib"].mean()
            inhibition_error = df["percent_inhib"].std()
            realind = index +1
            yield [(u"  Compound Concentration %d (uM) (Compound Concentration Range) " % realind, concentration ,),
                     (u"  Compound Concentration %d Inhibition (%%) (Compound Concentration Range) " % realind, inhibition ,),
                     (u"  Compound Concentration %d Error (%%) (Compound Concentration Range) " % realind, inhibition_error ,)]
        while index < 12:
            index += 1
            #Fill in any missing values up to 12 columns in total
            realind = index +1
            yield [(u"  Compound Concentration %d (uM) (Compound Concentration Range) " % realind , "" ,),
                 (u"  Compound Concentration %d Inhibition (%%) (Compound Concentration Range) " % realind, "" ,),
                 (u"  Compound Concentration %d Error (%%) (Compound Concentration Range) " % realind, "" ,)]
            

    def get_upload_to(self, name):
        return "%s/plates/%d/compounds/%s/%s" % (settings.MEDIA_ROOT, 
            self.data_mapping_revision_id, 
            self.compound_id, 
            name)

    def get_curve_fitter(self):

        group_df = read_json(self.raw_data)

        group_df.sort(["percent_inhib","concentration"], inplace=True)
        curve_fitter = IC50CurveFit(main_group_df=group_df)
        curve_fitter.get_fit(self, constrained=True)
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
        if self.comment != self.GOOD_CURVE:
            return 'ic50-error-4'
        else:
            return ""
              




