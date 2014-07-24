from django.shortcuts import render, redirect
from django.views.generic import View,  DetailView, ListView, CreateView
from django.views.generic.detail import SingleObjectMixin

from braces.views import LoginRequiredMixin

from django.db.models import get_model
from workflow.forms import CreateWorkflowForm, DataMappingForm, DataMappingFormSetHelper, DataMappingFormSet, ResetButton
from django.core.urlresolvers import reverse
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset, Reset
from django.http import HttpResponseRedirect
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib as mpl
import matplotlib.pyplot as plt
from workflow.forms import PlotForm

class WorkflowView( LoginRequiredMixin):

    model = get_model("workflow", "Workflow")

    def get_queryset(self):
        '''Make sure that all of the views cannot see the object unless they own it!'''
        return self.model.objects.get_user_records(self.request.user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(WorkflowView, self).get_context_data(**kwargs)
        context['revisions'] = {"upload" :"DSFDFSDF"}
        return context


class WorkflowListView(WorkflowView, ListView):
    '''Lists only the workflows that belong to that user'''
    template_name = "workflows/workflow_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(WorkflowListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books

        
        if context['object_list'].count() <= 11:
            context["first_eleven"] = list(context['object_list'])


        if context['object_list'].count() > 11:
            context["first_eleven"] = context['object_list'][0:10]
            context['object_list'] = context['object_list'][11:]
        else:
            context['object_list'] =[]
        return context


    def post(self, request, *args, **kwargs):
        pass




class WorkflowCreateView(WorkflowView, CreateView ):
    '''creates a single workflow'''
    fields = ['title', 'uploaded_file']
    template_name = "workflows/workflow_create.html"
    form_class = CreateWorkflowForm
    success_url = 'success'

    def get_success_url(self):
        return reverse('workflow_data_mappings_edit', kwargs={
                'pk': self.object.pk,
                })

    def form_valid(self, form):
        user = self.request.user
        form.instance.created_by = user
        form_valid = super(WorkflowCreateView, self).form_valid(form)
        
        if get_model("workflow", "workflowdatamappingrevision").objects.get_mapping_revisions_for_workflow(self.object).count() == 0:
            self.object.create_first_data_revision()

        return form_valid





class WorkflowDetailView(WorkflowView, DetailView, ):
    pass



class WorkflowOperationChooser(WorkflowDetailView):
    '''Allows the user to choose what to do with their data'''
    def get(self, request, *args, **kwargs):
        return render(request,
            "workflows/workflow_operation_chooser.html")

    def post(self, request, *args, **kwargs):
        pass






class WorkflowDataMappingEditView(WorkflowDetailView):
    '''Allows the user to edit the data mappings created automatically for the data they import'''
    template_name = "workflows/workflow_data_mapping_edit.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(WorkflowDataMappingEditView, self).get_context_data(**kwargs)
        context["graph"] = ""
        context["use_as_x_axis"] = ""
        context["use_as_y_axis"] = ""
        if not "formset" in kwargs:
            context["formset"] = DataMappingFormSet(initial=self.object.get_data_mapping_formset_data())
        context.update(kwargs)
        helper = DataMappingFormSetHelper()
        helper.template = 'table_inline.html'
        for mapping in GRAPH_MAPPINGS:
            helper.add_input(Submit(mapping, GRAPH_MAPPINGS[mapping]["name"]))

        helper.add_input(Submit("other", "Other"))
        helper.add_input(ResetButton("reset", "Reset Form"))

        context["helper"] = helper
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = DataMappingFormSet(request.POST)
        if formset.is_valid():
            data_changed = False
            for form in formset:
                if "dtype" in form.changed_data or "name" in form.changed_data:
                    data_changed = True
            if data_changed == True:
                steps_json = [{"cleaned_data" : form.cleaned_data, "changed_data" : form.changed_data }  for form in formset]
                new_workflow_revision = self.object.validate_columns(steps_json)
            graph = None
            for mapping in GRAPH_MAPPINGS:
                if mapping in formset.data:
                    graph = mapping
            return self.render_to_response(self.get_context_data(formset=formset, 
                                                                    graph=graph, 
                                                                    x_axis=formset.get_column_name_from_boolean("use_as_x_axis"),
                                                                    y_axis=formset.get_column_name_from_boolean("use_as_y_axis")))
        return self.render_to_response(self.get_context_data(formset=formset))

GRAPH_MAPPINGS = {
    "bar" : {"name": "Bar Graph", "function" : sns.barplot},
    "scatter" : {"name": "Scatter Graph", "function" : plt.scatter},
    "hist" : {"name": "Histogram", "function" : plt.hist},
    "boxplot" : {"name": "Boxplot", "function" : sns.boxplot},
}