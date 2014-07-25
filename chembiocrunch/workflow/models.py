from django.db import models
from pandas.io.pytables import get_store
from django_extensions.db.models import TimeStampedModel
from backends import dataframe_handler
from pandas import DataFrame, read_hdf
from django.db.models import get_model
from django.template.defaultfilters import slugify
import json

import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas





GRAPH_MAPPINGS = {
    "bar" : {"name": "Bar Graph", "function" : sns.barplot},
    "scatter" : {"name": "Scatter Graph", "function" : plt.scatter},
    "hist" : {"name": "Histogram", "function" : plt.hist},
    "boxplot" : {"name": "Boxplot", "function" : sns.boxplot},
}




def zero_pad_object_id(id):
    return ('%d' % id).zfill(11)



class WorkflowManager(models.Manager):
    def get_user_records(self, user):
        return self.filter(created_by__id=user.id)


    def get_latest_workflow_revision(self, workflow_id):
        return get_model("workflow", "WorkflowDataMappingRevision").objects.filter(workflow_id=workflow_id).order_by("-created")[0]

def my_slug(str):
    slugify(str.replace("-","_"))


# Create your models here.
class Workflow(TimeStampedModel):
    title = models.CharField(max_length=100)
    uploaded_file = models.FileField()
    created_by = models.ForeignKey('auth.User')
    objects = WorkflowManager()

    def get_latest_data_revision(self):
        return get_model("workflow", "Workflow").objects.get_latest_workflow_revision(self.id)

    def create_first_data_revision(self):

        df = dataframe_handler.get_data_frame(self.uploaded_file.file)
        new_workflow_revision = get_model("workflow", "WorkflowDataMappingRevision").objects.create(workflow=self, revision_type=UPLOAD, steps_json=json.dumps({"count" : int(df.count()[0])}))
        
        # types_frame = DataFrame([[str(dtype) for dtype in df.dtypes],], columns=df.dtypes.keys())

        df.to_hdf(new_workflow_revision.get_store_filename("data"), new_workflow_revision.get_store_key(), mode='w', format="table")
        # types_frame.to_hdf(new_workflow_revision.get_store_filename("dtypes"), new_workflow_revision.get_store_key(), mode='w', format="table")


        
        
    def validate_columns(self, steps_json):
        current_data_revision = self.get_latest_data_revision()
        df = current_data_revision.get_data()
        if not df.empty:
            new_workflow_revision = get_model("workflow", "WorkflowDataMappingRevision").objects.create(workflow=self, revision_type=VALIDATE_COLUMNS, steps_json=json.dumps(steps_json))
            df = dataframe_handler.change_all_columns(df, steps_json)
            df.to_hdf(new_workflow_revision.get_store_filename("data"), new_workflow_revision.get_store_key(), mode='w', format="table")
            print new_workflow_revision.id




    def get_data_mapping_formset_data(self):
        rev = self.get_latest_data_revision()
        df = rev.get_data()
        extra_data = [{"workflow_id": self.id, "column_id": index,  "name" : name ,"data_type" : df.dtypes[index].name } for index, name in enumerate(df.dtypes.keys())]
        return extra_data





    # def data_requires_update(self):
    #     '''
    #     method will test if the files attached to the class or the child pages have been updated since the data was last updated
    #     '''

    #     last_rev = self.last_data_revision()
    #     if last_rev == False:
    #         return True
    #     data_files_revisied = self.source_data_files.filter(modified__gte=last_rev.modified).count()
    #     if data_files_revisied > 0:
    #         return True
    #     return False


    # def last_data_revision(self):
    #     revisions = WorkflowDataMappingRevision.objects.fbarilter(page_id=self.id).order_by("-modified")
    #     if revisions.count() > 0:
    #         return revisions[0]
    #     return False


    # def current_es_client(self):
    #     '''Only to be used after an index was created by tasks.py'''
    #     last_revision = self.last_data_revision()
    #     es_processor = ElasticSearchDataProcessor(self.id, last_revision.id, {})
    #     return es_processor


    # def create_data_revision(self, new_steps_json, label=""):
    #     '''Generate a workflow revision using the list of steps in the json
    #     This might be an empty list if this is revision 1 for the particular dataset'''
    #     return WorkflowDataMappingRevision.objects.create(page=self, steps_json=json.dumps(new_steps_json), label=label)
        # pd = get_data_frame(uploaded_file)
        # if pd.columns.size <2:
        #     forms.ValidationError('Error with file, less than two columns recognised')
        # if pd.count()[0] < 1:
        #     forms.ValidationError('Error with file, zero rows recognised or first column empty')
    


    # @classmethod
    # def primary_input_file_fields(cls):
    #     #for later when we get forms working
    #     return ["testing1", "testing2"]

class WorkflowDataMappingRevisionManager(models.Manager):
    def get_mapping_revisions_for_workflow(self, workflow):
        return self.filter(workflow__id=workflow.id)

UPLOAD ="up"
VALIDATE_COLUMNS ="vc"

REVISION_TYPES = (
    (UPLOAD, "Upload"),
    (VALIDATE_COLUMNS, "Validate Columns")
)

class WorkflowDataMappingRevision(TimeStampedModel):

    '''Every time there is a major change to the mapping type in elasticsearch we reindex
    This object is designed to store the UI side definition of that change, which is translatable 
    to a reindex and remapping operation in elasticsearch'''
    '''In case of doing a statistics operation
    First we choose some columns 
    then we choose agregations
    then we reindex the agregated data
    All of these are steps in a single WorkflowDataMappingRevision
    '''

    workflow = models.ForeignKey('Workflow', related_name='workflow_data_revisions')
    steps_json = models.TextField(default="[]")
    revision_type = models.CharField(max_length=5)


    objects = WorkflowDataMappingRevisionManager()
    
    def get_store(self):
        return get_store('workflows.%s' % (zero_pad_object_id(self.workflow_id),))

    
    def get_store_filename(self, key,):
        return 'workflows.%s.%s' % (zero_pad_object_id(self.workflow_id),key)

    def get_store_key(self):
        return "wfdr%s" % (  zero_pad_object_id(self.id),)

    def get_dtypes(self, where=None):
        if not where:
            filename=self.get_store_filename("dtypes")
            print filename
            return read_hdf(filename,self.get_store_key(),)
        else:
            return read_hdf(self.get_store_filename("dtypes"),self.get_store_key(),where=where)




    def get_data(self, where=None):
        if not where:
            filename=self.get_store_filename("data")
            return read_hdf(filename,self.get_store_key(),)
        else:
            return read_hdf(self.get_store_filename("data"),self.get_store_key(),where=where)





class VisualisationManager(models.Manager):
    def by_workflow(self, workflow):
        return self.filter(data_mapping_revision__workflow_id=workflow.id).order_by("-modified")




class Visualisation(TimeStampedModel):
    GRAPH_TYPE_CHOICES = [(key, value["name"]) for key, value in GRAPH_MAPPINGS.iteritems()]
    data_mapping_revision = models.ForeignKey('WorkflowDataMappingRevision', related_name="data_revisions")
    x_axis = models.CharField(max_length=200)
    y_axis = models.CharField(max_length=200)
    visualisation_type = models.CharField(max_length=10, choices=GRAPH_TYPE_CHOICES)
    config_json = models.TextField(default="[]")
    objects = VisualisationManager()


    def get_column_form_data(self):
        df = self.data_mapping_revision.get_data()
        fields = df.columns.to_series().groupby(df.dtypes).groups
        fields_dict = {k.name: v for k, v in fields.items()}
        string_field_uniques = []
        for field in fields_dict["object"]:
            s = df[field].value_counts()
            string_field_uniques.append({"name": field, "choices" : [(k,k) for k,v in s.iterkv()]})
        numeric_field_max_and_min = []
        for field in fields_dict["int64"] + fields_dict["float64"]:
            numeric_field_max_and_min.append({"name" : field, "max" : s.max(), "min" : s.min()})

        return {"string_field_uniques" : string_field_uniques,"numeric_field_max_and_min" :numeric_field_max_and_min , "names" : [(name,name) for name in df.dtypes.keys()]}

    def get_initial_form_data(self):
        return { "x_axis" : self.x_axis, "y_axis":self.y_axis }



# class WorkflowDataColumnsRevision(TimeStampedModel):
#     '''Every time that there is a column added in elasticsearch then this object is designed to store the 
#     Column add and remove process which yields also a version id for the mapping type'''
#     schema_revision = models.ForeignKey('WorkflowDataMappingRevision', related_name="data_revisions")
#     steps_json = models.TextField(default="[]")



# class UserColumnDataMapping(TimeStampedModel):
#     CATEGORY = "ca"
#     FULLTEXT = "ft"
#     DATE = "da"
#     FLOAT = "fl"
#     DATA_TYPE_CHOICES = (
#         (CATEGORY, "Category"),
#         (FULLTEXT, "Full Text"),
#         (DATE, "Date"),
#         (FLOAT, "Decimal Number"),
#         )
#     DATA_TYPE_PANDAS_LOOKUP = {

#     }
#     '''A user is expected to maintain a list of the columns they use and the type of data in them
#     The contents of a new column description will be predicted based on previous ones but the scientist will not
#     be forced to change their previous version'''
#     name = models.CharField(max_length=250)
#     slug = models.CharField(max_length=250)
#     created_by = models.ForeignKey('auth.User')
#     data_type = models.CharField(max_length=2, choices=DATA_TYPE_CHOICES)



# class WorkflowDataMappingRevisionColumnLink(TimeStampedModel):
#     '''Links a revision of a set of mapping types to one of the Users' columns'''

#     user_column_data_mapping = models.ForeignKey(UserColumnDataMapping)
#     workflow_data_column_revision = models.ForeignKey(WorkflowDataColumnsRevision)

#     class Meta():
#         verbose_name = "WDCR linked to UCDM"
