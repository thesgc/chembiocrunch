#from django import forms    
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset, Reset
from django.db.models import get_model 
import magic
from backends.parser import get_data_frame
from crispy_forms.bootstrap import PrependedText
from django.forms.formsets import formset_factory, BaseFormSet
from workflow.backends.dataframe_handler import change_column_type

import floppyforms as forms






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
    #description = forms.CharField(max_length=400, required=False, show_hidden_initial=True)
    unit = forms.CharField(max_length=10, required=False, show_hidden_initial=True)
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
            #'description',
            'unit',
            Field('use_as_x_axis', css_class='use_as_x_axis'),
            Field('use_as_y_axis', css_class='use_as_y_axis'),
            )
        )
        self.render_required_fields = True


class ResetButton(Reset):
    field_classes = 'btn btn-danger'

class BaseDataMappingFormset(BaseFormSet):
    def get_column_name_from_boolean(self, boolean_field_name):
        for form in self:
            if form.cleaned_data.get(boolean_field_name, None):
                return form.cleaned_data.get("name", None)


    def clean(self):
        names = [form.cleaned_data["name"] for form in self]
        print names
        if len(names) > len(list(set(names))):
            raise forms.ValidationError('The name field must be unique across the fields')

        if not self.get_column_name_from_boolean("use_as_x_axis") or not self.get_column_name_from_boolean("use_as_y_axis"):
            raise forms.ValidationError('You need to select an x and y axis in order to plot data')


    # def clean(self):
    #     for form in self:
    #         for field_name in form.changed_data:
    #             print "field {} has changed. New value {}".format(field_name, form.cleaned_data[field_name])



class StringFieldFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        column_data = kwargs.pop('column_data')
        super(StringFieldFilterForm, self).__init__(*args, **kwargs)
        self.fields["filter_by"] = forms.MultipleChoiceField(        
            choices = column_data["choices"],
            widget = forms.CheckboxSelectMultiple,
        )


class NumericFieldFilterForm(forms.Form):
    pass





class VisualisationForm(forms.Form):
    PUBLICATION_TYPE_CHOICES = (("paper","Paper"),
                                ("talk", "Talk"),
                                ("notebook", "Notebook"),
                                ("poster", "Poster"))
    visualisation_title = forms.CharField(max_length=50)
    #x_axis = forms.ChoiceField( choices=[])
    #y_axis = forms.ChoiceField( choices=[])
    #split_y_axis_by = forms.ChoiceField(choices=[])
    #split_x_axis_by = forms.ChoiceField( choices=[])
    height = forms.FloatField(widget=Slider)
    aspect_ratio = forms.FloatField(widget=Slider)
    publication_type = forms.ChoiceField(choices=PUBLICATION_TYPE_CHOICES)
    error_bars = forms.BooleanField(required=False)
    
    def clean_height(self):
        height = self.cleaned_data['height']
        if not Slider.min <= height <= Slider.max:
            raise forms.ValidationError("Enter a value between 5 and 20")

        return height
    



    def __init__(self, *args, **kwargs):
        column_data = kwargs.pop('column_data')
        super(VisualisationForm, self).__init__(*args, **kwargs)
        # self.fields["x_axis"] = forms.ChoiceField(choices=column_data["names"])
        # self.fields["y_axis"] = forms.ChoiceField(choices= column_data["names"])
        # self.fields["split_x_axis_by"] = forms.ChoiceField( choices= column_data["names"])
        # self.fields["split_y_axis_by"] = forms.ChoiceField( choices= column_data["names"])
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Button('save', 'Submit'))
        self.helper.add_input(Button('export', 'Export to PPT'))
        self.helper.layout = Layout(
            Fieldset( 'Customise Visualisation',
                'visualisation_title', 
                'height',
                'aspect_ratio',
                'error_bars',
                'publication_type',
         )
        )
        
        self.request = kwargs.pop('request', None)
        #return self








DataMappingFormSet = formset_factory(DataMappingForm, extra=0, formset=BaseDataMappingFormset)
