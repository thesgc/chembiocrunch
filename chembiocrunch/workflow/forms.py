#from django import forms    
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset, Reset
from django.db.models import get_model 
import magic
from crispy_forms.bootstrap import PrependedText
from django.forms.formsets import formset_factory, BaseFormSet
from workflow.backends.dataframe_handler import change_column_type, get_data_frame

#from easy_select2.widgets import Select2TextInput
from django_select2.fields import Select2ChoiceField

import floppyforms as forms
from workflow.models import VALIDATE_COLUMNS, my_slug, GRAPH_MAPPINGS

import django.forms as vanillaforms


import json

import mpld3
import copy 

class Slider(forms.RangeInput):
    min = 0.2
    max = 5
    step = 0.2
    template_name = 'slider.html'

    class Media:
        js = (
            'js/jquery.min.js',
            'js/jquery-ui.min.js',
        )
        css = {
            'all': (
                'css/jquery-ui.css',
            )
        }

"http://filamentgroup.com/lab/update-jquery-ui-slider-from-a-select-element-now-with-aria-support.html"




class CreateWorkflowForm(forms.ModelForm):
    title = forms.CharField(max_length=50)
    uploaded_file = forms.FileField()

    def clean_uploaded_file(self):
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
            choices=DATA_TYPE_CHOICES,
        )

    
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
            current_data_revision.save()
            return current_data_revision
        return None



# class FilterForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         column_data = kwargs.pop('column_data')
#         super(FilterForm, self).__init__(*args, **kwargs)
#         fields = []
#         fieldsets = []
#         for field_data in column_data["string_field_uniques"]:
#             field = my_slug(field_data["name"])
#             self.fields[field] = forms.MultipleChoiceField( 
#                 choices = field_data["choices"],
#                 widget = forms.CheckboxSelectMultiple,
#                 initial = [choice[0] for choice in field_data["choices"]], #If initial data here
#                 required=False,
#             )
#             fields.append(field)
#             fieldsets.append(Fieldset('Filter %s' % field_data["name"], field ))

        
#         self.helper = FormHelper()
#         self.helper.add_input(Submit('submit', 'Filter'))
#         self.helper.layout = Layout(
#             *fieldsets
#         )
#         self.request = kwargs.pop('request', None)
#         self.helper.form_show_labels = False


# class NumericFieldFilterForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         column_data = kwargs.pop('column_data')
#         super(NumericFieldFilterForm, self).__init__(*args, **kwargs)
#         fields = []
#         for field_data in column_data["string_field_uniques"]:
#             field = my_slug(field_data["name"])
#             self.fields[field] = forms.MultipleChoiceField( 
#                 choices = field_data["choices"],
#                 widget = forms.CheckboxSelectMultiple,
#                 initial = [choice[0] for choice in field_data["choices"]],
#                 required=False,
#             )
#             fields.append(field)
#         print self
#         arguments = ['Label Filters',] + fields
#         self.helper = FormHelper()
#         self.helper.add_input(Button('submit', 'Filter'))
#         self.helper.layout = Layout(
#             Fieldset( 
#                *arguments
#             )     
#         )
#         self.request = kwargs.pop('request', None)
   





class VisualisationForm(forms.Form):
    PUBLICATION_TYPE_CHOICES = (("paper","Paper"),
                                ("talk", "Talk"),
                                ("notebook", "Notebook"),
                                ("poster", "Poster"))
    visualisation_title = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'placeholder': 'Visualisation Title'}), required=False)
    #x_axis = forms.ChoiceField( choices=[])
    #y_axis = forms.ChoiceField( choices=[])

    # height = forms.FloatField(widget=Slider)
    # aspect_ratio = forms.FloatField(widget=Slider)
    # publication_type = forms.ChoiceField(choices=PUBLICATION_TYPE_CHOICES)
    error_bars =  forms.TypedChoiceField(
        choices = ((1, "Yes"), (0, "No")),
        coerce = lambda x: bool(int(x)),
        widget = forms.RadioSelect,
        initial = '0',
        required = True,
    )
    visualisation_type = forms.ChoiceField(
        label = "",
        #choices = [(key, "Graph type: " +value["name"]) for key, value in GRAPH_MAPPINGS.iteritems()],
        choices = [("bar" , "Graph type: bar")],
        widget = forms.RadioSelect,
        initial = 'bar',
        required = True,
    )

    def save(self, data_mapping_revision, visualisation=None):
        Visualisation = get_model("workflow", "visualisation")
        cleaned_data = self.cleaned_data
        defaults = {    
                        fieldname: cleaned_data.pop(fieldname) 
                        for fieldname in ["visualisation_title",
                                            "visualisation_type",
                                           "error_bars",
                                           "x_axis",
                                           "y_axis",
                                           "split_x_axis_by",
                                           "split_y_axis_by",
                                            ]
                    }
        defaults["data_mapping_revision"] = data_mapping_revision
        config_json = self.cleaned_data
        defaults["config_json"] = json.dumps(config_json)
        print defaults
        if not visualisation:
            visualisation = Visualisation(**defaults)
            visualisation.html = mpld3.fig_to_html(visualisation.get_fig_for_dataframe())
            visualisation.save()
        else:
            
            qs = Visualisation.objects.filter(id=visualisation.id)
            qs.update(**defaults)
            visualisation = qs.get()
            visualisation.html = mpld3.fig_to_html(visualisation.get_fig_for_dataframe())
            visualisation.save()

        return visualisation





    def __init__(self, *args, **kwargs):
        column_data = kwargs.pop('column_data')
        
        super(VisualisationForm, self).__init__(*args, **kwargs)
        self.fields = copy.deepcopy(self.base_fields)

        self.fields["x_axis"] = forms.ChoiceField(choices=column_data["names"], initial=column_data["x_axis"])
        self.fields["y_axis"] = forms.ChoiceField(choices= column_data["names"], initial=column_data["y_axis"])
        self.fields["split_x_axis_by"] = forms.TypedChoiceField(initial=column_data.get("split_x_axis_by", None), 
                                                                required=False,
                                                                choices= [(None,"Do not split x axis"),] + [(label[0], "Split x axis by %s" % label[1]) for label in column_data["names"]])
        self.fields["split_y_axis_by"] = forms.TypedChoiceField(required=False, 
                                                                initial=column_data.get("split_y_axis_by", None), 
                                                                choices= [(None,"Do not split y axis"),] + [(label[0], "Split y axis by %s" % label[1]) for label in column_data["names"]])
        
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_tag = False
        #self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', 'Update and Save'))
        # self.helper.add_input(Button('export', 'Export to PPT'))
        self.helper.layout = Layout(
            Fieldset( 'Chart Options',
                'visualisation_title', 
                'visualisation_type', 
            ),
            Fieldset( 'X axis ',
                'x_axis',
                'split_x_axis_by',),
            Fieldset('Y axis ',
                'y_axis',
                'split_y_axis_by',  
            ),
            Fieldset(
                'Error bars',
                'error_bars',
            )
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
            fieldsets.append(Fieldset('Filter %s' % field_data["name"], field ))

        
        self.filterhelper = FormHelper()
        self.filterhelper.add_input(Submit('submit', 'Filter and Save'))
        self.filterhelper.layout = Layout(
            *fieldsets
        )
        self.filterhelper.form_show_labels = False
        if len(args) == 1:
            self.data = args[0]










DataMappingFormSet = formset_factory(DataMappingForm, extra=0, formset=BaseDataMappingFormset)
