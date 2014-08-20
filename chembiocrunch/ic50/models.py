from django.db import models
from django.db import models
from pandas.io.pytables import get_store
from django_extensions.db.models import TimeStampedModel
from pandas import DataFrame, read_hdf
from django.db.models import get_model
from django.template.defaultfilters import slugify
import json

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
from ic50.curve_fit import IC50CurveFit

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
        return self.filter(created_by__id=user.id)

    def get_latest_workflow_revision(self, workflow_id):
        return get_model("ic50", "IC50WorkflowRevision").objects.filter(workflow_id=workflow_id).order_by("created")[0]


class IC50Workflow(TimeStampedModel):
    title = models.CharField(max_length=100)
    uploaded_config_file = models.FileField(max_length=1024)
    uploaded_data_file = models.FileField(max_length=1024)
    uploaded_meta_file = models.FileField(max_length=1024)
    created_by = models.ForeignKey('auth.User')
    objects = IC50WorkflowManager()

    #def get_latest_data_revision(self):
    #    return get_model("workflow", "Ic50Workflow").objects.get_latest_workflow_revision(self.id)



    def get_latest_workflow_revision(self):
        return get_model("ic50", "IC50WorkflowRevision").objects.filter(workflow_id=self.id).order_by("-created")[0]










        #this is where auto-munging of data can take place
        #i.e. any ipython workflows applied here

        #df becomes the result of data munging? Do that elsewhere?

        #df = dataframe_handler.get_data_frame(self.uploaded_file.file)
        #new_workflow_revision = get_model("workflow", "IcFiftyWorkflowDataMappingRevision").objects.create(workflow=self, revision_type=UPLOAD, steps_json=json.dumps({"count" : int(ddf.count()[0]) }))

        # types_frame = DataFrame([[str(dtype) for dtype in df.dtypes],], columns=df.dtypes.keys())

        #dcf.to_hdf(new_workflow_revision.get_store_filename("data"), new_workflow_revision.get_store_key(), mode='w', format="table")
        #ddf.to_hdf(new_workflow_revision.get_store_filename("data"), new_workflow_revision.get_store_key(), mode='w', format="table")
        # types_frame.to_hdf(new_workflow_revision.get_store_filename("dtypes"), new_workflow_revision.get_store_key(), mode='w', format="table")





class IC50WorkflowRevision(TimeStampedModel):

    '''
    Revision for IC50 workflows
    '''

    workflow = models.ForeignKey('IC50Workflow', related_name='workflow_ic50_revisions')
    plate_name = models.CharField(max_length=30, default="")
    steps_json = models.TextField(default="[]")

    def previous(self):
        '''Get the previous item belongin to this workflow'''
        qs = self.workflow.workflow_ic50_revisions.filter(pk__lt=self.id).order_by("-pk")
        if qs.count() == 0:
            return None
        else:
            return qs[0]

    def next(self):
        '''Get the next item belonging to this workflow'''
        qs = self.workflow.workflow_ic50_revisions.filter(pk__gt=self.id).order_by("pk")
        if qs.count() == 0:
            return None
        else:
            return qs[0]


    def create_ic50_data(self):
        config = self.get_config_data()
        sample_codes = config.groupby(["fullname"])
        data = self.get_data()
        excl = json.loads(self.steps_json)
        print excl
        config_columns = data.apply(
            get_config_columns,
            args=(sample_codes,excl),
            axis=1
        )
        config_columns[["figure"]] = config_columns[["figure"]].astype(float)
        minimum = min(config_columns["figure"])
        config_columns["percent_inhib"] = config_columns["figure"] * 0
        #
        ic50_groups = config_columns.groupby("global_compound_id")
        controls = ic50_groups.get_group("NONE")

        for ic50_group in ic50_groups.groups:
            if ic50_group != "NONE":

                group_df = ic50_groups.get_group(ic50_group)
                group_well_letters = [k for k,v in group_df["well_letter"].value_counts().iterkv()]
                if group_df['well_number'].max() > 12:
                    column = 24
                else:
                    column = 12
                group_full_refs = ["%s%d" % (letter , column) for letter in group_well_letters]
                group_controls = controls[controls["full_ref"].isin(group_full_refs)]
                group_max = group_controls["figure"].mean()
                group_df["percent_inhib"] =  100*(group_max - group_df["figure"] )/(group_max - minimum)
                group_df.sort(["percent_inhib","concentration"], inplace=True)
                self.plot_ic50(group_df,ic50_group)

    def plot_ic50(self, group_df, ic50_group):
        curve_fitter = IC50CurveFit(group_df)
        for constrained in (True,):
            if constrained:
                title = "%s" % ic50_group
            #else:
             #   title = "%s (unconstrained)" % ic50_group

            fit = curve_fitter.get_fit(constrained=constrained)

            vis = IC50Visualisation(data_mapping_revision=self,
                                compound_id=ic50_group,
                                results=json.dumps({"values": curve_fitter.results}),
                                constrained=constrained,
                                visualisation_title=title,
                                html=curve_fitter.svg)
            vis.save()





    def get_store(self):
        return get_store('workflows.%s' % (zero_pad_object_id(self.id),))


    def get_store_filename(self,dtype ):
        return 'ic50_workflows%s.%s' % (dtype, zero_pad_object_id(self.workflow_id))

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















    # @classmethod
    # def primary_input_file_fields(cls):
    #     #for later when we get forms working
    #     return ["testing1", "testing2"]





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
    l'''
    data_mapping_revision = models.ForeignKey('IC50WorkflowRevision', related_name="visualisations")
    x_axis = models.CharField(max_length=200, default="Destination Concentration")
    y_axis = models.CharField(max_length=200, default='Percent inhibition')
    compound_id = models.CharField(max_length=200)
    error_bars = models.NullBooleanField()
    results = models.TextField(default="{}")
    visualisation_title = models.CharField(max_length=200, null=True, blank=True) #Will be used for the sample name
    config_json = models.TextField(default="{}")
    html = models.TextField(default="")
    constrained = models.NullBooleanField()
    objects = IC50VisualisationManager()


    def get_svg(self):
        imgdata = StringIO()
        fig = self.get_fig_for_dataframe()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)
        return imgdata.buf


