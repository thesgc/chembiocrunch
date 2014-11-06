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
from cbc_common.dataframe_handler import cell_range,  get_data_frame, get_excel_data_frame

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


from datetime import datetime
import time
import re


class IC50UploadForm(forms.ModelForm):

    '''This is (sort of) an abstract class. Extend this if you are creating an IC50 related workflow
    FILES will not validate correctly unless the temporary uploaded file file upload handler has been set
    in the settings
    '''
    title = forms.CharField(max_length=50)
    uploaded_data_file = forms.FileField(label="BMG output file")
    uploaded_config_file = forms.FileField(label="ESXX transfer file")
    uploaded_meta_file = forms.FileField(label="Assay metadata file")
    #also needa field which holds the "type", obtained from the URL
    form_type = None
    uploaded_config = None
    uploaded_data = None
    uploaded_meta = pd.DataFrame()
    plates = []
    included_plate_wells = None
    reference_compound_wells = None
    control_wells = cell_range("C12:P12,C24:P24")
    exclude = ["reference_compound_wells", "control_wells"]


    class Meta:
        model = get_model('ic50', "IC50Workflow")
        exclude = ('created_by','form_type')


    def clean(self):
        self.plates = []
        # try:
        indexed_config = self.uploaded_config
        indexed_config_groups = indexed_config.groupby("plate_ref")

        #indexed_config = indexed_config.set_index('fullname')
        
        #fully_indexed = data_with_index_refs.set_index('fullname')
        #Assumed that datafile contains only one plate worth of data
        #Sort by the plate reference to create plates in order
        self.uploaded_data.sort(["plate_ref"], inplace=True)
        data_groups = self.uploaded_data.groupby("plate_ref")
        for name, grouped in data_groups:
            #Iterate the names and groups in the dataset
            if name in indexed_config_groups.groups:
                print "found this %s" % str(name)
                config = indexed_config_groups.get_group(name)
                wells = [str(row) for row in config["full_ref"] ]
                included_plate_wells = set(wells)
                inc_wells = {}
                for item in grouped["full_ref"]:
                    if item in included_plate_wells:
                        inc_wells[str(item)] = True
                    else:
                        inc_wells[str(item)] = None
                self.plates.append({"plate_name": name, "data" : grouped, "config" : config, "steps_json": inc_wells} )
        if len(self.plates) == 0:
            raise forms.ValidationError("No plate references match between the transfer file and the output file, please ensure the files come from the same experiment")


    def save(self, force_insert=False, force_update=False, commit=True):
        model = super(IC50UploadForm, self).save()
        model.set_meta_data(self.uploaded_meta)
        # do custom stuff
        for plate in self.plates:
            self.save_plate(model, plate)
        return model





    def save_plate(self,model, plate):  
        new_workflow_revision = get_model("ic50", "IC50WorkflowRevision").objects.create(workflow=model, 
                                                                                        steps_json=json.dumps(plate["steps_json"]),
                                                                                        plate_name=str(plate["plate_name"]),
                                                                                        )
        included_wells = [datum for datum in plate["steps_json"] if plate["steps_json"][datum]]
        config = plate["config"]
        data = plate["data"]

        config = config[config['global_compound_id'].notnull()]
        possible_control_records = plate["config"][plate["config"]['global_compound_id'].isnull()]["full_ref"].tolist()

        controls_records = data[data["full_ref"].isin(included_wells) & data["full_ref"].isin(self.control_wells) & data["full_ref"].isin(possible_control_records)]
        solvent_controls_records = data[~data["full_ref"].isin(included_wells) & data["full_ref"].isin(self.control_wells) & data["full_ref"].isin(possible_control_records)]
        maximum = controls_records["figure"].mean()
        maximum_error = controls_records["figure"].std()
        solvent_maximum = solvent_controls_records["figure"].mean()
        solvent_maximum_error = solvent_controls_records["figure"].std()

        config_columns = config.merge(data, on="full_ref")
        config_columns["status"] = "active"
        config_columns[["figure"]] = config_columns[["figure"]].astype(float)
        minimum = 0 # Add min controls here
        minimum_error = 0
        if self.reference_compound_wells:
            reference_compound_records = data[data["full_ref"].isin(included_wells) & data["full_ref"].isin(self.reference_compound_wells)]
            minimum = reference_compound_records["figure"].mean()
            minimum_error = reference_compound_records["figure"].std()
        new_workflow_revision.minimum = minimum
        new_workflow_revision.minimum_error = minimum_error
        new_workflow_revision.maximum = maximum
        new_workflow_revision.maximum_error = maximum_error
        new_workflow_revision.solvent_maximum = solvent_maximum
        new_workflow_revision.solvent_maximum_error = solvent_maximum_error      

        config_columns["percent_inhib"] =  (maximum - config_columns["figure"] )/(maximum - minimum)
        #sort by plate ref in order to create the items in order
        config_columns.sort("full_ref", inplace=True)
        ic50_groups = config_columns.groupby("global_compound_id")
        for ic50_group in ic50_groups.groups:
            if ic50_group != "NONE":
                group_df = ic50_groups.get_group(ic50_group)
                raw_data = group_df.to_json()
                vis = get_model("ic50", "IC50Visualisation")(data_mapping_revision_id=new_workflow_revision.id,
                            compound_id=ic50_group,
                            raw_data=raw_data,
                            constrained=True,
                            visualisation_title=ic50_group,
                            html="")
                vis.save()
        plate["data"].to_hdf(new_workflow_revision.get_store_filename("data"), new_workflow_revision.get_store_key(), mode='w')
        config_columns.to_hdf(new_workflow_revision.get_store_filename("configdata"),new_workflow_revision.get_store_key(), mode='w')
        new_workflow_revision.save()


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
        # self.request = kwargs.pop('request')
        return super(IC50UploadForm, self).__init__(*args, **kwargs)


    def clean_uploaded_data_file(self):
        raise forms.ValidationError("No processing code has been implemented for this file")

    def clean_uploaded_config_file(self):
        raise forms.ValidationError("No processing code has been implemented for this file")

    def clean_uploaded_meta_file(self):
        raise forms.ValidationError("No processing code has been implemented for this file")



def get_plate_ref(dfseries):
    '''split out the square backets to give the plate reference'''
    split = dfseries.str.split(r"\[").str.get(1)
    split = split.str.encode("ascii", "ignore")
    return split








class LabCyteEchoIC50UploadForm(IC50UploadForm):
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
        self.request = kwargs.pop('request')
        return super(LabCyteEchoIC50UploadForm, self).__init__(*args, **kwargs)


    def clean_uploaded_data_file(self):
        '''This method cleans the incoming data file and converts it to a pandas DataFrame
        The column names from the original data file are not used
        The data file is returned as is standard in Django so that the form can be re submitted if there is an error somewhere
        The output dataframe is expected to contain this data schema:
        "fullname" - whatever the original full name of the plate well + plate was
        "figure" - the raw total transmision measurement from the plate reader
        "full_ref" - the well code i.e. A1
        "plate_ref" - any letter or number that can be used to match this plate with the plates in the liquid handler transfer file for multiplate experiments
        if it is not a multiplate experiment simply fill this field with 0 on both data frames 
        "well_letter" - the letter of the well row
        "well number" - the number of the plate column (extracted here by regex)
        '''
        uploaded_data_file = self.files['uploaded_data_file']
        mime = magic.from_buffer(self.files["uploaded_data_file"].read(), mime=True)
        if 'text/' in mime:
            try:
                self.uploaded_data = get_data_frame(uploaded_data_file.temporary_file_path())
            except AttributeError:
                raise forms.ValidationError('Cuploaded_configannot access the file during upload due to application misconfiguration. Please consult the application administrator and refer them to the documentation on github')
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

        self.uploaded_data.columns = ["fullname","figure",]
        refs = self.uploaded_data["fullname"].str.split(':')
        self.uploaded_data["full_ref"] = refs.str.get(1).str.strip()
        self.uploaded_data["plate_ref"] = get_plate_ref(refs.str.get(0).str.strip())
        matches = self.uploaded_data["full_ref"].str.findall(r"([A-Z]+)([0-9]+)")
        self.uploaded_data["well_letter"] = matches.str.get(0).str.get(0)
        self.uploaded_data["well_number"] = matches.str.get(0).str.get(1)

        return self.cleaned_data['uploaded_data_file']



    def clean_uploaded_config_file(self):
        '''This method takes an uploaded config file and converts it to a pandas dataframe, 
        it returns the file as is the convention in django
        The final config dataframe should have the following columns:
        "fullname" - whatever the original full name of the plate well + plate was
        "full_ref" - the well code i.e. A1
        "plate_ref" - any letter or number that can be used to match this plate with the plates in the liquid handler transfer file for multiplate experiments
        if it is not a multiplate experiment simply fill this field with 0 on both data frames 
        "global_compound_id" - an id for the compounds being tested. Note that by default if the compound is 
        subjected to duplicate assays on the same plate this will be treated as a single assay and all the points plotted on one curve'''
        uploaded_config_file = self.files['uploaded_config_file']
        mime = magic.from_buffer(self.files["uploaded_config_file"].read(), mime=True)
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
                except Exception:
                    raise forms.ValidationError("Error processing config Excel File")
            except AttributeError:
                raise forms.ValidationError('Cannot access the file during upload due to application misconfiguration. Please consult the application administrator and refer them to the documentation on github')
        else:
            raise forms.ValidationError('File must be in CSV, XLS or XLSX format')
        self.uploaded_config["fullname"] = self.uploaded_config["Destination Plate Name"] + ": " + self.uploaded_config["Destination Well"]
        self.uploaded_config["full_ref"] = self.uploaded_config["Destination Well"]
        self.uploaded_config["plate_ref"] = get_plate_ref(self.uploaded_config["Destination Plate Name"])
        self.uploaded_config["global_compound_id"] = self.uploaded_config["Sample ID"]
        self.uploaded_config["concentration"] = self.uploaded_config["Destination Concentration"] * float(1000000)
        self.uploaded_config["plate_type"]  = self.uploaded_config["Destination Plate Type"]
        #filter for only the appropirate liquid handler plate type
        self.uploaded_config = self.uploaded_config[self.uploaded_config["plate_type"].isin(["Proxiplate_384PS",])]
        return self.cleaned_data['uploaded_config_file']



    def clean_uploaded_meta_file(self):
        '''Currently this method looks for the control wells and refference compound wells
        in the metadata file as it is uploaded and sets them as attributes of the objects
        By The default control wells are in columns 12 and 24 excluding rows A and B#
        By default there are no reference compound wells and it is assumed that the minimum transmitance is zero
        The cell ranges are specified in Excel format using colons and commas to separate e.g. A1:A3,A5,A7'''
        uploaded_meta_file = self.files.get('uploaded_meta_file', False)
        if uploaded_meta_file:
            mime = magic.from_buffer(uploaded_meta_file.read(), mime=True)
            if 'text/' in mime:
                try:
                    self.uploaded_meta = get_data_frame(uploaded_meta_file.temporary_file_path())
                except AttributeError:
                    raise forms.ValidationError('Cannot access the file during upload due to application misconfiguration. Please consult the application administrator and refer them to the documentation on github')
                except Exception:
                        raise forms.ValidationError("Error processing meta CSV File")
            elif "application/" in mime:
                try:
                    try:
                        self.uploaded_meta = get_excel_data_frame(uploaded_meta_file.temporary_file_path())

                    except Exception:
                        raise forms.ValidationError("Error processing meta Excel File")
                except AttributeError:
                    raise forms.ValidationError('Cannot access the file during upload due to application misconfiguration. Please consult the application administrator and refer them to the documentation on github')
            else:
                raise forms.ValidationError('File must be in CSV, XLS or XLSX format')
            if not self.uploaded_meta.empty:
                controls = self.uploaded_meta[self.uploaded_meta[4].str.lower().isin(["control wells"]) & self.uploaded_meta[5].notnull()]
                if not controls.empty:
                    self.control_wells = cell_range(controls[5].tolist()[0])
                else:
                    raise forms.ValidationError("Control well cell ranges should be in the meta data file")
                refs = self.uploaded_meta[self.uploaded_meta[4].str.lower().isin(["reference compound wells"]) & self.uploaded_meta[5].notnull()]
                if not refs.empty:
                    self.reference_compound_wells = cell_range(refs[5].tolist()[0])
            return self.cleaned_data['uploaded_meta_file']
        return None








class TemplateIC50UploadForm(IC50UploadForm):




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
        self.request = kwargs.pop('request')
        return super(TemplateIC50UploadForm, self).__init__(*args, **kwargs)

    def clean_uploaded_data_file(self):
        '''This method cleans the incoming data file and converts it to a pandas DataFrame
        The column names from the original data file are not used
        The data file is returned as is standard in Django so that the form can be re submitted if there is an error somewhere
        The output dataframe is expected to contain this data schema:
        "fullname" - whatever the original full name of the plate well + plate was
        "figure" - the raw total transmision measurement from the plate reader
        "full_ref" - the well code i.e. A1
        "plate_ref" - any letter or number that can be used to match this plate with the plates in the liquid handler transfer file for multiplate experiments
        if it is not a multiplate experiment simply fill this field with 0 on both data frames 
        "well_letter" - the letter of the well row
        "well number" - the number of the plate column (extracted here by regex)
        '''
        pass



    def clean_uploaded_config_file(self):
        '''This method takes an uploaded config file and converts it to a pandas dataframe, 
        it returns the file as is the convention in django
        The final config dataframe should have the following columns:
        "fullname" - whatever the original full name of the plate well + plate was
        "full_ref" - the well code i.e. A1
        "plate_ref" - any letter or number that can be used to match this plate with the plates in the liquid handler transfer file for multiplate experiments
        if it is not a multiplate experiment simply fill this field with 0 on both data frames 
        "global_compound_id" - an id for the compounds being tested. Note that by default if the compound is 
        subjected to duplicate assays on the same plate this will be treated as a single assay and all the points plotted on one curve'''
        pass



    def clean_uploaded_meta_file(self):
        '''Currently this method looks for the control wells and refference compound wells
        in the metadata file as it is uploaded and sets them as attributes of the objects
        By The default control wells are in columns 12 and 24 excluding rows A and B#
        By default there are no reference compound wells and it is assumed that the minimum transmitance is zero
        The cell ranges are specified in Excel format using colons and commas to separate e.g. A1:A3,A5,A7'''
        pass





def human(num):
    num = int(num)
    if num > 1000000000:
        return "%dbn" % (num / 1000000000)
    if num > 1000000:
        return "%dm" % (num / 1000000)
    if num > 10000:
        return "%dk" % (num / 1000)
    else:
        return num









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
        )
        #set up a column header helper containing checkboxes to deselct every well in a column
        column_helper = HeatmapFormHelper()
        column_helper.layout=Layout(
            HTML('<tr><td>&nbsp;</td>')
        )
        element_list = ['<tr><td>&nbsp;</td>' ,]
        for letter in well_letters:
            #create table row
            loopels = []
            loophelper = HeatmapFormHelper()
            loophelper.layout = Layout()
            loophelper.layout.fields.extend([
                HTML('<tr>')
            ])
            loopels.append('<tr>')
            self.fields['header_' + str(letter)] = forms.BooleanField(initial=False, label=letter, required=False)
            loophelper.layout.fields.extend([
                    HTML('<th data_row="' + str(letter) + '" class="hmp_row_header">'),
                    'header_' + str(letter),
                    HTML('</th>')
                ])
            temp = '<div class="form-group"><div id="div_id_header_%s" class="checkbox"><label for="id_header_%s" class=""><input type="checkbox" name="header_%s" class="checkboxinput checkbox" id="id_header_%s">%s</label></div></div>' % (letter,letter,letter,letter,letter)
            loopels.append('<th data_row="' + str(letter) + '" class="hmp_row_header">' + temp +'</th>')
            #loop through subset of ud which has that letter
            subset = ud[ud['well_letter'] == letter]
            subset = subset.convert_objects(convert_numeric=True).sort("well_number")
            rows_list = []
            for index, row in subset.iterrows():
                well_str = row['well_letter'] + str(row['well_number'])
                #work out the class number to apply for conditional formatting -
                #an integer between 1-10 worked out from the fraction this value is of the maximum

                try:
                    row_list = []
                    initial = j.pop(well_str)
                    condclassint = int(math.ceil((float(row['figure']) / float(hi_value)) * 10))
                    cond_class = str(condclassint)
                    disable_attrs = {}
                    if not initial:
                        cond_class += " unchecked"
                        disable_attrs = {'disabled':'disabled'}
                    field = forms.BooleanField(initial=initial, required=False, label=int(row['figure']), widget=forms.CheckboxInput(attrs=disable_attrs))
                    self.fields[well_str] = field
                    loophelper.layout.fields.extend([
                        HTML('<td data_row="' + row['well_letter'] + '" data_column="' + str(row['well_number']) + '" class="hide-checkbox hmp' + cond_class + '">'),
                        well_str,
                        HTML('</td>')
                    ])
                    checked = ""
                    if initial:
                        checked ="checked"
                    cell_temp = '<div class="form-group"><div id="div_id_%s" class="checkbox"><label for="id_%s" class=""><input type="checkbox" name="%s" %s class="checkboxinput checkbox" id="id_%s">%s </label></div></div>' % (well_str, well_str,well_str, checked , well_str, human(row['figure']))
                    loopels.append('<td data_row="' + row['well_letter'] + '" data_column="')
                    loopels.append(str(row['well_number']) + '" class="hide-checkbox hmp' + cond_class + '">' + cell_temp + '</td>')
                    #add a table heading cell for each column - only do this for the first row
                    if (letter == 'A'):
                        self.fields['header_' + str(row['well_number'])] = forms.BooleanField(initial=False, required=False, label=row['well_number'])
                        column_helper.layout.fields.extend([
                                HTML('<th data_column="' + str(row['well_number']) + '" class="hmp_header">'),
                                'header_' + str(row['well_number']),
                                HTML('</th>')
                            ])
                        template = '<div class="form-group"><div id="div_id_header_%d" class="checkbox"><label for="id_header_%d" class=""><input type="checkbox" name="header_%d" class="checkboxinput checkbox" id="id_header_%d">%d</label></div></div>' % (row['well_number'], row['well_number'], row['well_number'], row['well_number'], row['well_number'])

                        element_list.append('<th data_column="' + str(row['well_number']) + '" class="hmp_header">')
                        element_list.append(template + '</th>')
                    cond_class = ""
                except KeyError:
                    #value already popped
                    pass
            #this may have to change to reflect how the row names have been assigned - will work for 99% of current examples though
            if(letter == 'A'):
                self.helper.layout.append(column_helper.layout)

            self.helper.layout.append(loophelper.layout)
            element_list.extend("".join(loopels))
            self.element_list = "".join(element_list)




FORM_REGISTRY = {"LabcyteEcho" : LabCyteEchoIC50UploadForm ,
                 #   "Template" : TemplateIC50UploadForm
                    }

