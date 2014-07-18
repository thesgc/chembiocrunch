from django import forms    
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset
from django.db.models import get_model 
import magic
from backends.parser import get_data_frame


class CreateWorkflowForm(forms.ModelForm):
    title = forms.CharField(max_length=50)
    uploaded_file  = forms.FileField()

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