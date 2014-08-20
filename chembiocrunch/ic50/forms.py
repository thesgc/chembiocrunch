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
from cbc_common.dataframe_handler import change_column_type, get_data_frame, get_excel_data_frame, get_plate_wells_with_sample_ids

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

from cbc_common.dataframe_handler import get_ic50_data_columns, get_ic50_config_columns









class IC50UploadForm(forms.ModelForm):

    '''This is (sort of) an abstract class. Extend this if you are creating an IC50 related workflow
    FILES will not validate correctly unless the temporary uploaded file file upload handler has been set
    in the settings
    '''
    title = forms.CharField(max_length=50)
    uploaded_data_file = forms.FileField(label="BMG output file")
    uploaded_config_file = forms.FileField(label="ESXX transfer file")
    uploaded_meta_file = forms.FileField(required=False)
    #also needa field which holds the "type", obtained from the URL
    form_type = None
    uploaded_config = None
    uploaded_data = None
    uploaded_meta = None
    included_plate_wells = None


    class Meta:
        model = get_model('ic50', "IC50Workflow")
        exclude = ('created_by','form_type')


    def clean_uploaded_data_file(self):
        #TODO validate datafile tocheck only one plate present
        uploaded_data_file = self.files['uploaded_data_file']
        mime = magic.from_buffer(self.files["uploaded_data_file"].read(), mime=True)
        print mime
        if 'text/' in mime:
            try:
                self.uploaded_data = get_data_frame(uploaded_data_file.temporary_file_path())
            except AttributeError:
                raise forms.ValidationError('Cannot access the file during upload due to application misconfiguration. Please consult the application administrator and refer them to the documentation on github')
            except Exception:
                    raise forms.ValidationError("Error processing data Excel File")
        elif "application/" in mime:
            try:
                self.uploaded_data = get_excel_data_frame(uploaded_data_file.temporary_file_path())
            except AttributeError:
                raise forms.ValidationError('Cannot access the file during upload due to application misconfiguration. Please consult the application administrator and refer them to the documentation on github')
            except Exception:
                    raise forms.ValidationError("Error processing data Excel File")
        else:
            raise forms.ValidationError('File must be in CSV, XLS or XLSX format')
        return self.cleaned_data['uploaded_data_file']


    def clean_uploaded_config_file(self):
        uploaded_config_file = self.files['uploaded_config_file']
        mime = magic.from_buffer(self.files["uploaded_config_file"].read(), mime=True)
        print mime
        if 'text/' in mime:
            try:
                self.uploaded_config = get_data_frame(uploaded_config_file.temporary_file_path(), skiprows=8, header=0)
            except AttributeError:
                raise forms.ValidationError('Cannot access the file during upload due to application misconfiguration. Please consult the application administrator and refer them to the documentation on github')
            except Exception:
                    raise forms.ValidationError("Error processing config CSV File")
        elif "application/" in mime:
            try:
                try:
                    self.uploaded_config = get_excel_data_frame(uploaded_config_file.temporary_file_path(), skiprows=8, header=0)
                    #self.uploaded_config["full_ref"] = self.uploaded_config["Destination Well"]
                    #self.uploaded_config = self.uploaded_config[self.uploaded_config["Source Plate Name"]=="Intermediate Sample Plate[1]"]
                except Exception:
                    raise forms.ValidationError("Error processing config Excel File")
            except AttributeError:
                raise forms.ValidationError('Cannot access the file during upload due to application misconfiguration. Please consult the application administrator and refer them to the documentation on github')
        else:
            raise forms.ValidationError('File must be in CSV, XLS or XLSX format')
        return self.cleaned_data['uploaded_config_file']

    # def clean_uploaded_meta_file(self):
    #     uploaded_meta_file = self.files.get('uploaded_meta_file', False)
    #     if uploaded_meta_file:
    #         mime = magic.from_buffer(uploaded_meta_file.read(), mime=True)
    #         print mime
    #         if 'text/' in mime:
    #             try:
    #                 self.uploaded_meta = get_data_frame(uploaded_meta_file.temporary_file_path(), skiprows=8, header=0)
    #             except AttributeError:
    #                 raise forms.ValidationError('Cannot access the file during upload due to application misconfiguration. Please consult the application administrator and refer them to the documentation on github')
    #             except Exception:
    #                     raise forms.ValidationError("Error processing config CSV File")
    #         elif "application/" in mime:
    #             try:
    #                 try:
    #                     self.uploaded_meta = get_excel_data_frame(uploaded_meta_file.temporary_file_path(), skiprows=8, header=0)
    #                     print self.uploaded_meta.dtypes.keys()
    #                 except Exception:
    #                     raise forms.ValidationError("Error processing config Excel File")
    #             except AttributeError:
    #                 raise forms.ValidationError('Cannot access the file during upload due to application misconfiguration. Please consult the application administrator and refer them to the documentation on github')
    #         else:
    #             raise forms.ValidationError('File must be in CSV, XLS or XLSX format')
    #         return self.cleaned_data['uploaded_meta_file']
    #     return None



    def clean(self):
        indexed_config = self.uploaded_config.apply(get_ic50_config_columns, axis=1)
        #indexed_config = indexed_config.set_index('fullname')
        data_with_index_refs = self.uploaded_data.apply(get_ic50_data_columns, axis=1)
        #fully_indexed = data_with_index_refs.set_index('fullname')
        #Assumed that datafile contains only one plate worth of data
        self.uploaded_data = data_with_index_refs
        self.uploaded_config = indexed_config

        wells = [str(row) for row in indexed_config["Destination Well"]]

        included_plate_wells = set(wells)
        inc_plates = {}
        for item in data_with_index_refs["full_ref"]:
            if item in included_plate_wells:
                inc_plates[str(item)] = True
            else:
                inc_plates[str(item)] = None
        self.included_plate_wells = inc_plates



    def save(self, force_insert=False, force_update=False, commit=True):
        model = super(IC50UploadForm, self).save()
        # do custom stuff
        model.create_first_data_revision(self.uploaded_data, self.included_plate_wells, self.uploaded_config, self.uploaded_meta)
        model.save()
        return model


    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('save', 'Save'))
        self.helper.layout = Layout(
            Fieldset( '',
                'title', 'uploaded_data_file',
                'uploaded_config_file', 'uploaded_meta_file', 'save',
         )
        )
        self.request = kwargs.pop('request', None)
        return super(IC50UploadForm, self).__init__(*args, **kwargs)





class HeatmapFormHelper(FormHelper):
    form_show_labels = True
    form_tag = False


class HeatmapForm(forms.Form):

    def __init__(self, *args, **kwargs):
        ud = kwargs.pop('uploaded_data')
        j = kwargs.pop('steps_json')
        #j = json.loads(hj)
        super(HeatmapForm, self).__init__(*args, **kwargs)

        self.helper = HeatmapFormHelper()
        ud[["figure"]] = ud[["figure"]].astype(float)
        hi_value = ud['figure'].max()
        well_letters = ud['well_letter'].unique()

        self.helper.layout=Layout(
            HTML('<div class="table-responsive"><table class="heatmap">')
        )
        #set up a column header helper containing checkboxes to deselct every well in a column
        column_helper = HeatmapFormHelper()
        column_helper.layout=Layout(
            HTML('<tr><td>&nbsp;</td>')
        )
        for letter in well_letters:
            #create table row
            loophelper = HeatmapFormHelper()
            loophelper.layout = Layout()
            loophelper.layout.fields.extend([
                HTML('<tr>')
            ])
            self.fields['header_' + str(letter)] = forms.BooleanField(initial=False, label=letter, required=False)
            loophelper.layout.fields.extend([
                    HTML('<th data_row="' + str(letter) + '" class="hmp_row_header">'),
                    'header_' + str(letter),
                    HTML('</th>')
                ])
            #loop through subset of ud which has that letter
            subset = ud[ud['well_letter'] == letter]
            subset = subset.convert_objects(convert_numeric=True).sort("well_number")
            for index, row in subset.iterrows():
                well_str = row['well_letter'] + str(row['well_number'])
                #work out the class number to apply for conditional formatting -
                #an integer between 1-10 worked out from the fraction this value is of the maximum

                try:

                    initial = j.pop(well_str)
                    condclassint = int(math.ceil((float(row['figure']) / float(hi_value)) * 10))
                    cond_class = str(condclassint)
                    disable_attrs = {}
                    if not initial:
                        cond_class += " unchecked"
                        disable_attrs = {'disabled':'disabled'}

                    self.fields[well_str] = forms.BooleanField(initial=initial, required=False, label=int(row['figure']), widget=forms.CheckboxInput(attrs=disable_attrs))
                    loophelper.layout.fields.extend([
                        HTML('<td data_row="' + row['well_letter'] + '" data_column="' + str(row['well_number']) + '" class="hide-checkbox hmp' + cond_class + '">'),
                        well_str,
                        HTML('</td>')
                    ])
                    #add a table heading cell for each column - only do this for the first row
                    if (letter == 'A'):
                        self.fields['header_' + str(row['well_number'])] = forms.BooleanField(initial=False, required=False, label=row['well_number'])
                        column_helper.layout.fields.extend([
                                HTML('<th data_column="' + str(row['well_number']) + '" class="hmp_header">'),
                                'header_' + str(row['well_number']),
                                HTML('</th>')
                            ])
                    #print cond_class
                    cond_class = ""
                except KeyError:
                    #value already popped
                    pass
            #this may have to change to reflect how the row names have been assigned - will work for 99% of current examples though
            if(letter == 'A'):
                self.helper.layout.append(column_helper.layout)
            self.helper.layout.append(loophelper.layout)
        stop_helper = HeatmapFormHelper()

        stop_helper.layout=Layout(
            HTML('</table></div>'),
            "save"
        )
        self.helper.layout.append(stop_helper)
        self.helper.add_input(Submit('save', 'Save'))
        self.helper.layout.append("save")
