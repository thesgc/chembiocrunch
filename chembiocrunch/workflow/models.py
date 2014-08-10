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

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from StringIO import StringIO

from seaborn import plotting_context, set_context
import mpld3
from workflow.basic_units import BasicUnit


def get_labels(vis, df):
    return sorted([k for k,v in df[vis.x_axis].value_counts().iterkv()])

def get_none(vis, df):
    return None


#Graph mappings allow the choices field for graphs to be populated and also tell the plotting algo which seaborn function to use as we plot data
GRAPH_MAPPINGS = {
    "bar" : {"xy": False, "name": "Bar", "function" : sns.barplot, "get_label_function" : get_labels},
    "point" : {"xy": False, "name": "Point Plot", "function" : sns.pointplot, "get_label_function" : get_labels},

    "scatter" : {"xy": True, "name": "Scatter", "function" : plt.scatter, "get_label_function" : get_none},
    "linear_reg" : {"xy": True, "name": "Linear Regression", "function" : sns.regplot, "get_label_function" : get_none},
   # "hist" : {"name": "Histogram", "function" : plt.hist},
   # "boxplot" : {"name": "Boxplot", "function" : sns.boxplot},
}




def zero_pad_object_id(id):
    '''used to ensure data files appear in order of ID'''
    return ('%d' % id).zfill(11)



class WorkflowManager(models.Manager):
    '''Manager allows extra functions to be added to the objects of a model so that you can run queries without having to 
    do the query logic inline'''
    def get_user_records(self, user):
        '''Used to filter in view to ensure only permitted workflows are seen'''
        return self.filter(created_by__id=user.id)

    def get_latest_workflow_revision(self, workflow_id):
        return get_model("workflow", "WorkflowDataMappingRevision").objects.filter(workflow_id=workflow_id).order_by("-created")[0]

def my_slug(str):
    return slugify(str).replace("-","_")

class BaseWorkflow(TimeStampedModel):
    pass
    class Meta:
        abstract = True

# Create your models here.
class Workflow(TimeStampedModel):
    '''A workflow is a container for a set of graphs based on one file. It will have its sub objects cloned
    when the user wants a similar graphing dashboard'''
    title = models.CharField(max_length=100)
    uploaded_file = models.FileField()
    created_by = models.ForeignKey('auth.User')
    objects = WorkflowManager()

    def get_latest_data_revision(self):
        return get_model("workflow", "Workflow").objects.get_latest_workflow_revision(self.id)

    def create_first_data_revision(self):

        df = dataframe_handler.get_data_frame(self.uploaded_file.file)
        new_workflow_revision = get_model("workflow", "WorkflowDataMappingRevision").objects.create(workflow=self, revision_type=UPLOAD)   
        # types_frame = DataFrame([[str(dtype) for dtype in df.dtypes],], columns=df.dtypes.keys())
        df.to_hdf(new_workflow_revision.get_store_filename("data"), new_workflow_revision.get_store_key(), mode='w', format="table")
        # types_frame.to_hdf(new_workflow_revision.get_store_filename("dtypes"), new_workflow_revision.get_store_key(), mode='w', format="table")


                



    def get_data_mapping_formset_data(self):
        rev = self.get_latest_data_revision()
        df = rev.get_data()
        extra_data = [{"workflow_id": self.id, "column_id": index,  "name" : name ,"data_type" : df.dtypes[index].name } for index, name in enumerate(df.dtypes.keys())]
        return extra_data



# PB - new Workflow for IC50 project.
class IcFiftyWorkflowManager(models.Manager):
    def get_user_records(self, user):
        return self.filter(created_by__id=user.id)


    def get_latest_workflow_revision(self, workflow_id):
        return get_model("workflow", "IcFiftyWorkflowDataMappingRevision").objects.filter(workflow_id=workflow_id).order_by("-created")[0]


class IcFiftyWorkflow(TimeStampedModel):
    title = models.CharField(max_length=100)
    uploaded_config_file = models.FileField()
    uploaded_data_file = models.FileField()    
    created_by = models.ForeignKey('auth.User')
    objects = WorkflowManager()

    def get_latest_data_revision(self):
        return get_model("workflow", "IcFiftyWorkflow").objects.get_latest_workflow_revision(self.id)

    def create_first_data_revision(self):
        
        dcf = dataframe_handler.get_data_frame(self.uploaded_config_file.file)
        ddf = dataframe_handler.get_data_frame(self.uploaded_data_file.file)

        #this is where auto-munging of data can take place
        #i.e. any ipython workflows applied here

        #df becomes the result of data munging? Do that elsewhere?

        #df = dataframe_handler.get_data_frame(self.uploaded_file.file)
        new_workflow_revision = get_model("workflow", "IcFiftyWorkflowDataMappingRevision").objects.create(workflow=self, revision_type=UPLOAD, steps_json=json.dumps({"count" : int(ddf.count()[0]) }))
        
        # types_frame = DataFrame([[str(dtype) for dtype in df.dtypes],], columns=df.dtypes.keys())

        dcf.to_hdf(new_workflow_revision.get_store_filename("data"), new_workflow_revision.get_store_key(), mode='w', format="table")
        ddf.to_hdf(new_workflow_revision.get_store_filename("data"), new_workflow_revision.get_store_key(), mode='w', format="table")
        # types_frame.to_hdf(new_workflow_revision.get_store_filename("dtypes"), new_workflow_revision.get_store_key(), mode='w', format="table")

    def get_data_mapping_formset_data(self):
        rev = self.get_latest_data_revision()
        df = rev.get_data()
        extra_data = [{"workflow_id": self.id } ]
        return extra_data




    # def data_requires_update(self):
    #     '''
    #     method will test if the files attached to the class or the child pages have been updated since the data was last updated
    #     '''

    #     last_rev = self.last_data_revision()
    #     if last_rev == False:WorkflowDataMappingRevision
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


    # def current_es_client(self):WorkflowDataMappingRevision
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

    '''Every time there is a major change to the field names or the data types in 
    the columns of a workflow's data, we store a revision of the workflow.
    These revisions are as far as possible invisible to the user - we just want them to be able
    to switch between different graphs on a workflow not worrying if data is being treated as a label
    or a number.
    '''

    workflow = models.ForeignKey('Workflow', related_name='workflow_data_revisions')
    steps_json = models.TextField(default="[]")
    revision_type = models.CharField(max_length=5)
    x_axis = models.CharField(max_length=100)
    y_axis = models.CharField(max_length=100)
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

    def get_column_form_data(self):
        df = self.get_data()
        fields = df.columns.to_series().groupby(df.dtypes).groups
        fields_dict = {k.name: v for k, v in fields.items()}
        string_field_uniques = []
        choices_overall =  []
        for field in fields_dict.get("object",[]):
            s = df[field].value_counts()
            string_field_uniques.append({"name": field,"initial":[k for k,v in s.iterkv()], "choices" : [(k,k) for k,v in s.iterkv()]})
            choices_overall.append((field, "%s (label)" % field))
        numeric_field_max_and_min = []
        for field in fields_dict.get("float64",[]):
            numeric_field_max_and_min.append({"name" : field, "max" : s.max(), "min" : s.min(), "initial_min" :s.min(),"initial_max" : s.max() })
            choices_overall.append((field, "%s (decimal)" % field))
        for field in fields_dict.get("int64",[]):
            numeric_field_max_and_min.append({"name" : field, "max" : s.max(), "min" : s.min(), "initial_min" :s.min(),"initial_max" : s.max() })
            choices_overall.append((field, "%s (whole number)" % field))  

        return {
        "split_by": None,
        "split_x_axis_by": None,
        "split_y_axis_by": None,
        "visualisation_type" : "bar",
        "visualisation_title" : "",
        "x_axis": self.x_axis, "y_axis": self.y_axis, "string_field_uniques" : string_field_uniques,"numeric_field_max_and_min" :numeric_field_max_and_min , "names" : choices_overall}




class IcFiftyWorkflowDataMappingRevision(TimeStampedModel):

    '''

    '''

    workflow = models.ForeignKey('IcFiftyWorkflow', related_name='workflow_ic50_data_revisions')
    steps_json = models.TextField(default="[]")
    revision_type = models.CharField(max_length=5)
    x_axis = models.CharField(max_length=100)
    y_axis = models.CharField(max_length=100)
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
    '''Retrieves visible lists of workflows using the revision id'''
    def by_workflow(self, workflow):
        return self.filter(data_mapping_revision__workflow_id=workflow.id).order_by("-created")

    def by_workflow_revision(self, workflow_revision):
        return self.filter(data_mapping_revision_id=workflow_revision.id).order_by("-created")




class Visualisation(TimeStampedModel):
    '''Holder object for a visualisation
    loosely bound to the visulaisation form
    html field contains a cached svg representation of the visualisation'''
    GRAPH_TYPE_CHOICES = [(key, value["name"]) for key, value in GRAPH_MAPPINGS.iteritems()]
    data_mapping_revision = models.ForeignKey('WorkflowDataMappingRevision', related_name="data_revisions")
    x_axis = models.CharField(max_length=200)
    y_axis = models.CharField(max_length=200)
    split_by = models.CharField(max_length=200, null=True, blank=True, default=None)
    split_x_axis_by = models.CharField(max_length=200, null=True, blank=True, default=None)
    split_y_axis_by = models.CharField(max_length=200, null=True, blank=True, default=None)
    error_bars = models.NullBooleanField()
    visualisation_title = models.CharField(max_length=200, null=True, blank=True)
    visualisation_type = models.CharField(max_length=10, choices=GRAPH_TYPE_CHOICES)
    config_json = models.TextField(default="{}")
    html = models.TextField(default="")
    objects = VisualisationManager()


    def get_svg(self):
        imgdata = StringIO()
        fig = self.get_fig_for_dataframe()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)
        return imgdata.buf


    def get_fig_for_dataframe(self):
        form_data = self.get_column_form_data()
        string_expressions = {form_datum["name"] : form_datum["initial"] for form_datum in form_data["string_field_uniques"]}
        df = self.data_mapping_revision.get_data()
        row_mask = df.isin(string_expressions)[[form_datum["name"]  for form_datum in form_data["string_field_uniques"]]]
        df = DataFrame(df[row_mask.all(1)])
        split_y_axis_by = self.split_y_axis_by if self.split_y_axis_by !='None' else None
        split_x_axis_by = self.split_x_axis_by if self.split_x_axis_by !='None' else None

        kwargs = {"size": 6, 
                    "aspect": 1.7,
                     "sharex":True, 
                     "sharey":True, 
                    }
        split_by = self.split_by if self.split_by !='None' else None
        if split_by:
            kwargs["row"] = None
            kwargs["col"] = split_by
            kwargs["col_wrap"] = 4
        if GRAPH_MAPPINGS[self.visualisation_type]["xy"] == True:
            if df.count()[0] > 0 :
                xlim = (0, float(max(df[self.x_axis]))*1.1)
                ylim = (0, float(max(df[self.y_axis]))*1.1)
                kwargs["xlim"] = xlim
                kwargs["ylim"] = ylim
         

        with plotting_context( "talk" ):
            labels = GRAPH_MAPPINGS[self.visualisation_type]["get_label_function"](self, df) 
            # g = sns.factorplot(self.x_axis,
            #      y=self.y_axis, data=df, 
            #      row=self.split_y_axis_by if self.split_y_axis_by !='None' else None, 
            #      x_order=labels, 
            #      col=self.split_x_axis_by if self.split_x_axis_by !='None' else None,)
            g_kwargs = {}
            if labels:
                g_kwargs = {"x_order":labels}  
            print kwargs
            g = sns.FacetGrid(df,**kwargs )
            
            g.map(GRAPH_MAPPINGS[self.visualisation_type]["function"], self.x_axis, self.y_axis, **g_kwargs);
            if labels:
                if split_by:
                    for ax in g.axes:
                        ax.set_xticklabels(labels, rotation=90)
                else:
                    g.set_xticklabels(labels, rotation=90)

            #if labels and not split_by :
             #   g.set_xticklabels(labels, rotation=90) 
            if self.visualisation_title:
                g.fig.tight_layout()
                height_in_inches = g.fig.get_figheight()
                title_height_fraction = 0.2 / (height_in_inches ** (0.5)) #20px is ~0.3 inches
                g.fig.suptitle(self.visualisation_title, fontsize=20)
                g.fig.tight_layout(rect=(0,0,1,1 - title_height_fraction))
            else:
                g.fig.tight_layout()            
            g.fig.patch.set_alpha(0.0)
            return g.fig



    def get_column_form_data(self):
        df = self.data_mapping_revision.get_data()
        fields = df.columns.to_series().groupby(df.dtypes).groups
        fields_dict = {k.name: v for k, v in fields.items()}


        string_field_uniques = []
        config_json = json.loads(self.config_json)
        choices_overall = []
        for field in fields_dict.get("object",[]):
            s = df[field].value_counts()
            initial = []
            if config_json.get(my_slug(field)):
                initial = config_json.get(my_slug(field))
            else:
                initial = [k for k,v in s.iterkv()]
            string_field_uniques.append({"name": field,"initial": initial, "choices" : sorted([(k,k) for k,v in s.iterkv()])})
            choices_overall.append((field, "%s (label)" % field))
        numeric_field_max_and_min = []
        for field in fields_dict.get("float64",[]):
            numeric_field_max_and_min.append({"name" : field, "max" : s.max(), "min" : s.min(), "initial_min" :s.min(),"initial_max" : s.max() })
            choices_overall.append((field, "%s (decimal)" % field))
        for field in fields_dict.get("int64",[]):
            numeric_field_max_and_min.append({"name" : field, "max" : s.max(), "min" : s.min(), "initial_min" :s.min(),"initial_max" : s.max() })
            choices_overall.append((field, "%s (whole number)" % field))  

        return {
        "visualisation_type" : self.visualisation_type,
        "visualisation_title" : self.visualisation_title,
        "error_bars": self.error_bars, 
        "x_axis": self.x_axis, 
        "y_axis": self.y_axis,
        "split_by" : self.split_by, 
        "split_x_axis_by" : self.split_x_axis_by, 
        "split_y_axis_by" : self.split_y_axis_by, 
        "string_field_uniques" : string_field_uniques,
        "numeric_field_max_and_min" :numeric_field_max_and_min , 
        "names" : choices_overall}



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
