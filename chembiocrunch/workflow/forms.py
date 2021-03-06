# -*- coding: utf8 -*-
#from django import forms    
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset, Reset
from django.db.models import get_model 
import magic
from crispy_forms.bootstrap import (
PrependedAppendedText, AppendedText, PrependedText, InlineRadios,
Tab, TabHolder, AccordionGroup, Accordion, Alert, InlineCheckboxes,
FieldWithButtons, StrictButton, InlineField
)
from django.forms.formsets import formset_factory, BaseFormSet
from cbc_common.dataframe_handler import change_column_type, get_data_frame, get_excel_data_frame

#from easy_select2.widgets import Select2TextInput
from django_select2.fields import Select2ChoiceField

import floppyforms as forms
from workflow.models import VALIDATE_COLUMNS, my_slug, GRAPH_MAPPINGS

import django.forms as vanillaforms

import json

import mpld3
import copy
from workflow.basic_units import BasicUnit
import pandas as pd
import math
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.bootstrap import StrictButton
import pandas as pd


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('save', 'Sign in'))
        self.helper.layout = Layout(
            Fieldset( '',
            'username',
            'password',
            )
        )
        self.helper.form_tag = True




class Slider(forms.RangeInput):
    '''A slider input widget'''
    min = 0.2
    max = 5
    step = 0.2
    template_name = 'slider.html'

    class Media:
        js = (
            'js/jquery.min.jsget_ic50_data_columns',
            'js/jquery-ui.min.js',
        )
        css = {
            'all': (
                'css/jquery-ui.css',
            )
        }

"http://filamentgroup.com/lab/update-jquery-ui-slider-from-a-selectself.uploaded_data-element-now-with-aria-support.html"




class CreateWorkflowForm(forms.ModelForm):
    '''form that validates the file type of an uploaded file'''
    title = forms.CharField(max_length=50)
    uploaded_file = forms.FileField()

    def clean_uploaded_file(self):
        ''' it is necessary to test the file type of the file
        In order to clean the data of a field in django
        the method must raise new validation errors against that 
        particular field. The method naming convention is to name the function as 
        clean_[field name]
        IT is IMPERATIVE to return the data of the file'''
        uploaded_file = self.cleaned_data['uploaded_file']
        mime = magic.from_buffer(uploaded_file.read(), mime=True)
        if 'text/' not in mime:
            raise forms.ValidationError('File must be a CSV document')
       
        # pd = get_data_frame(uploaded_file)
        # if pd.columns.size <2:
        #     forms.ValidationError('Error with file, less than two columns recognised')
        # if pd.count()[0] < 1:
        #     forms.ValidationError('Error with file, zero rows recognised or first column empty')
        return uploaded_file

    class Meta:
        model = get_model("workflow", "workflow")
        exclude = ('created_by',)





    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('save', 'Save'))
        self.helper.layout = Layout(
            Fieldset( '',
                'title', 'uploaded_file', 
                'save',
         )
        )
        
        self.request = kwargs.pop('request', None)
        return super(CreateWorkflowForm, self).__init__(*args, **kwargs)




DATA_TYPE_CHOICES = (
    ("object", "Label"),
    ("float64", "Decimal Number"),
    ("int64", "Whole Number"),
)

UNIT_CHOICES = (
        ("", "Not applicable"),
  #      ("%", "% (specify of what)"),
        (" ", "Other (specify)"),
    ("mM", "millimolar (mM)"),
    ("μM", "micromolar (μl)"),
    ("nM", "nanomolar (nM)"),
    ("pM", "picomolar (pM)"),
    
    ("μl", "millilitre (μl)"),
    ("ml", "microlitre (ml)"),
    ("l", "litre (l)"),
    ("mol", "moles (M)"),
    ("Angstrom", "Angstrom (Å)"),
    ("K", "Kelivin (K)"),
    ("degrees-c", "degrees (°C)"),
    # ("g", "g"),
    # ("mg", "mg"),
    # ("kg", "kg"),
    #("nm", "nm"),
    #("m/s", "m/s")
)


UNIT_OBJECTS = { unit[0] : BasicUnit(unit[0],unit[1]) for unit in UNIT_CHOICES if unit[0] not in ["", "%", " "]}

class DataMappingForm(forms.Form):
    readonly_fields = ('name',)
    workflow_id = forms.IntegerField()
    column_id = forms.IntegerField()
    name = forms.CharField(max_length=100, show_hidden_initial=True)
    data_type = forms.ChoiceField(choices=DATA_TYPE_CHOICES, show_hidden_initial=True)
    # unit = vanillaforms.ChoiceField(widget = Select2TextInput(
    #         select2attrs={
    #             'data': [ {'id': 'data1', 'text': 'data1'}, {'id': 'data2', 'text': 'data2'} ],
    #         },
    #     ))
    #description = forms.CharField(max_length=400, required=False, show_hidden_initial=True)
    #unit = vanillaforms.ChoiceField()
    unit = Select2ChoiceField(
            choices=UNIT_CHOICES,
            required=False,
        )
    other_unit = forms.CharField(
        required=False,
    max_length=15, 
        show_hidden_initial=True, 
        widget=forms.TextInput(attrs={'placeholder': '', 'size':5}))
    
    use_as_x_axis = forms.BooleanField(required=False, show_hidden_initial=True)
    use_as_y_axis = forms.BooleanField(required=False, show_hidden_initial=True)

    def clean_data_type(self):
        if "data_type" in self.changed_data:
            data = self.cleaned_data["data_type"]
            df = get_model("workflow", "workflow").objects.get_latest_workflow_revision(self.cleaned_data["workflow_id"]).get_data()
            try:
                df = change_column_type(df,self.cleaned_data["column_id"], data)
            except ValueError:
                raise forms.ValidationError('The data in this field is not suitable for conversion to numbers')

    
    # def __init__(self, *args, **kwargs):
    #     super(DataMappingForm, self).__init__(*args, **kwargs)
    #     self.fields["unit"] = forms.ChoiceField(required=False)
    #     self.fields["unit"].widget = Select2TextInput(
    #         select2attrs={
    #             'data': [ {'id': 'data1', 'text': 'data1'}, {'id': 'data2', 'text': 'data2'} ],
    #         },
    #     )


class DataMappingFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(DataMappingFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            Fieldset(
            '',
            Field('workflow_id', type="hidden"),
            Field('column_id', type="hidden"),
            'name',
            'data_type',
            #'hide',
            'description',
            'unit',
            Field('other_unit',css_class='other_unit'),
            Field('use_as_x_axis', css_class='use_as_x_axis'),
            Field('use_as_y_axis', css_class='use_as_y_axis'),
            )
        )
        self.render_required_fields = True

class BigButton(Submit):
    field_classes = 'btn btn-default btn-large'

class ResetButton(Reset):
    field_classes = 'btn btn-danger'

class BaseDataMappingFormset(BaseFormSet):
    '''Base class for the formset which al;lows fields to be auto generated
    On save we create a new data mapping revision and then redirect the user to
    use that particular data mapping revision for their visualisation'''
    def get_column_name_from_boolean(self, boolean_field_name):
        for form in self:
            if form.cleaned_data.get(boolean_field_name, None):
                return form.cleaned_data.get("name", None)


    def get_data_type(self, boolean_field_name):
        for form in self:
            if form.cleaned_data.get(boolean_field_name, None) == True:
                return form.cleaned_data.get("data_type", None)
            else:
                continue

    def clean(self):
        names = [form.cleaned_data["name"] for form in self]
        if len(names) > len(list(set(names))):
            raise forms.ValidationError('The name field must be unique across the fields')

        if not self.get_column_name_from_boolean("use_as_x_axis") or not self.get_column_name_from_boolean("use_as_y_axis"):
            raise forms.ValidationError('You need to select an x and y axis in order to plot data')


    def process(self, workflow):
        data_changed = False
        for form in self:
            if "dtype" in form.changed_data or "name" in form.changed_data:
                data_changed = True
        steps_json = [{"cleaned_data" : form.cleaned_data, "changed_data" : form.changed_data }  for form in self]
        current_data_revision = workflow.get_latest_data_revision()
        x_axis = self.get_column_name_from_boolean("use_as_x_axis")
        y_axis = self.get_column_name_from_boolean("use_as_y_axis")
        if data_changed == True:
            df = current_data_revision.get_data()
            if not df.empty:
                new_workflow_revision = get_model("workflow", "WorkflowDataMappingRevision").objects.create(
                    workflow=workflow, 
                    revision_type=VALIDATE_COLUMNS, 
                    steps_json=json.dumps(steps_json),
                    x_axis=x_axis,
                    y_axis=y_axis,
                    )
                df = dataframe_handler.change_all_columns(df, steps_json)
                df.to_hdf(new_workflow_revision.get_store_filename("data"), 
                    new_workflow_revision.get_store_key(), 
                    mode='w', 
                    format="table")
                return new_workflow_revision

        else:
            #Not a data revision, we are just changing the default x and y axes
            current_data_revision.x_axis = x_axis
            current_data_revision.y_axis = y_axis
            current_data_revision.steps_json = json.dumps(steps_json)
            current_data_revision.revision_type = VALIDATE_COLUMNS
            current_data_revision.save()
            return current_data_revision
        return None






class VisualisationForm(forms.Form):
    '''The visualistion form has a whole set of auto-generated fields based upon whatever the
    schema of the uploaded file is. These fields are then distributed across the UI in such a way as to
    create a good user experience. The form is not bound as a modelform because
    it has to be completely generated on the fly anyway'''
    PUBLICATION_TYPE_CHOICES = (("paper","Paper"),
                                ("talk", "Talk"),
                                ("notebook", "Notebook"),
                                ("poster", "Poster"))



    def save(self, data_mapping_revision, visualisation=None):
        Visualisation = get_model("workflow", "visualisation")
        cleaned_data = self.cleaned_data
        defaults = {    
                        fieldname: cleaned_data.pop(fieldname) 
                        for fieldname in ["visualisation_title",
                                            "visualisation_type",
                                        #   "error_bars",
                                           "x_axis",
                                           "y_axis",
                                           "split_colour_by",
                                           "split_y_axis_by",
                                           "split_by",
                                            ]
                    }
        defaults["data_mapping_revision"] = data_mapping_revision
        config_json = self.cleaned_data
        defaults["config_json"] = json.dumps(config_json)
        if not visualisation:
            visualisation = Visualisation(**defaults)
            visualisation.html = visualisation.get_svg()
            visualisation.save()
        else:
            qs = Visualisation.objects.filter(id=visualisation.id)
            qs.update(**defaults)
            visualisation = qs.get()
            visualisation.html = visualisation.get_svg()
            visualisation.save()

        return visualisation





    def __init__(self, *args, **kwargs):
        column_data = kwargs.pop('column_data')
        
        super(VisualisationForm, self).__init__(*args, **kwargs)
        self.fields = copy.deepcopy(self.base_fields)
        self.fields["visualisation_title"] = forms.CharField(max_length=50,
            label="Title",
            widget=forms.TextInput(attrs={"size":1}), 
            required=False, 
            initial = column_data["visualisation_title"],
        )
        self.fields["visualisation_type"] = forms.ChoiceField(
            label = "",
            choices = [(key, value["name"]) for key, value in GRAPH_MAPPINGS.iteritems()],
            #choices = [("bar" , "Graph type: bar")],
            widget = forms.RadioSelect,
            initial = column_data["visualisation_type"],
            required = True,
        )
        split_y_axis_by = column_data["split_y_axis_by"]
        self.fields["split_y_axis_by"] = forms.ChoiceField(required=False,choices= column_data["names"], initial=column_data["y_axis"])
        split_colour_by = column_data["split_colour_by"]
        
        self.fields["split_colour_by"] = forms.ChoiceField(required=False,
            choices=[(None,"Do not split into colours"),] + [(label[0], "Split into colours by %s" % label[1]) for label in column_data["names"] if "label" in label[1]],
            initial=split_colour_by,   
            label="Split into colours by"  )

        self.fields["x_axis"] = forms.TypedChoiceField(
                                    choices= [(label[0], "x axis - %s" % label[1]) for label in column_data["names"]],
                                    initial=column_data["x_axis"], 
                                    required=False,
                                            )
        
        self.fields["y_axis"] = forms.TypedChoiceField(required=False, 
            choices= [ (label[0], "y axis - %s" % label[1]) for label in column_data["names"]],
                                                                initial=column_data["y_axis"], 
                                                                )

        split_by = column_data["split_by"]
        self.fields["split_by"] = forms.TypedChoiceField(required=False, 
            choices= [(None,"Do not split into multiples"),] + [(label[0], "Split into multiples by %s" % label[1]) for label in column_data["names"] if "label" in label[1]],
                                                                initial=split_by,   label="Split into multiples by"  )
        self.titlehelper = FormHelper()
        self.titlehelper.form_class = 'form-inline'
        self.titlehelper.field_template = 'bootstrap3/layout/inline_field.html'
        
        self.titlehelper.layout = Layout(
            Div(
            'visualisation_title',
            css_class="col-xs-3 col-sm-2"),
            
        )
             
        self.titlehelper.form_tag = False

        self.helper = FormHelper()
        #self.helper.form_show_labels = False
        self.helper.form_tag = False
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'

        self.helper.layout = Layout(
                Div('split_colour_by',css_class="col-lg-4 col-sm-4 col-xs-4"),
                Div('split_by',css_class="col-lg-4 col-sm-4 col-xs-4"),
                Div('x_axis',css_class="col-lg-3 col-sm-3 col-xs-3"),
                 Div(
                Submit('sub',"Update"),css_class="col-lg-1 col-sm-1 col-xs-1"
             )  
        )
        self.xhelper = FormHelper()
        #self.helper.form_show_labels = False
        self.xhelper.form_tag = False
        self.xhelper.form_class = 'form-inline'
        self.xhelper.field_template = 'bootstrap3/layout/inline_field.html'

        self.xhelper.layout = Layout(
                Div('y_axis',css_class="col-xs-3"),
                Div(
                InlineRadios('visualisation_type',),css_class="col-xs-9 col-sm-9"
            ),
        )
        fields = []
        fieldsets = []
        for field_data in column_data["string_field_uniques"]:
            field = my_slug(field_data["name"])
            self.fields[field] = forms.MultipleChoiceField( 
                choices = field_data["choices"],
                widget = forms.CheckboxSelectMultiple,
                initial = [choice for choice in field_data["initial"]], #If initial data here
                required=False,
            )
            fields.append(field)
            fieldsets.append(InlineCheckboxes(field ))

        
        self.filterhelper = FormHelper()
        self.filterhelper.add_input(Submit('submit', 'Filter'))
        fieldsets = ["",] + fieldsets
        self.filterhelper.layout = Layout(
            Fieldset( 
            *fieldsets
            )
        )
        self.filterhelper.form_show_labels = False
        if len(args) == 1:
            self.data = args[0]
        self.filterhelper.form_tag = False





DataMappingFormSet = formset_factory(DataMappingForm, extra=0, formset=BaseDataMappingFormset)
