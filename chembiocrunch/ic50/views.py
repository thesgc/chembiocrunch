from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View,  DetailView, ListView, CreateView
from django.views.generic.detail import SingleObjectMixin
from django.conf import settings

from braces.views import LoginRequiredMixin

from django.db.models import get_model
from .forms import  IC50UploadForm, HeatmapForm
from django.core.urlresolvers import reverse
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset, Reset
from django.http import HttpResponseRedirect, HttpResponse

import matplotlib

import matplotlib.pyplot as plt

import json

import seaborn as sns
from workflow.models import GRAPH_MAPPINGS
from seaborn import plotting_context, set_context
import mpld3
import pandas as pd
from django.forms import Form
from pptx import Presentation
from pptx.util import Inches, Px
# Create your views here.
class IC50WorkflowView(LoginRequiredMixin):

    model = get_model("ic50", "IC50Workflow")

    def get_queryset(self):
        '''Make sure that all of the views cannot see the object unless they own it!'''
        return self.model.objects.get_user_records(self.request.user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IC50WorkflowView, self).get_context_data(**kwargs)
        context['revisions'] = [["upload" ,"not-done"],
                                ["validate" ,"not-done"],
                                ["visualise", "not-done"],
                                ["customise" , "not-done"]]
        return context

class IC50WorkflowDetailView(IC50WorkflowView, DetailView, ):
    pass

class IC50WorkflowCreateView(IC50WorkflowView, CreateView ):
    '''creates a single workflow'''
    fields = ['title', 'uploaded_data_file','uploaded_config_file', 'uploaded_meta_file']
    template_name = "workflows/workflow_ic50_create.html"
    #form_class = LabcyteEchoIC50UploadForm
    form_class = IC50UploadForm
    model = get_model("ic50", "IC50Workflow")

    def get_success_url(self):
        return reverse('workflow_ic50_heatmap', kwargs={
                'pk': self.object.pk,
                'workflow_revision_id' : self.object.get_latest_workflow_revision().id,
                })

    def form_valid(self, form):
        user = self.request.user
        form.instance.created_by = user
        form_valid = super(IC50WorkflowCreateView, self).form_valid(form)

        return form_valid

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IC50WorkflowCreateView, self).get_context_data(**kwargs)
        context['revisions'][0][1] = "in-progress"
        return context




class Ic50UpdateView(IC50WorkflowDetailView):

    workflow_revision_id = None
    visualisation_id = None
    template_name = "visualise/visualisation_builder.html"

    def get_context_data(self,  **kwargs):
        # visualisation_form = None
        # if "visualisation_form" in kwargs:
        #     visualisation_form = kwargs.pop("visualisation_form")

        context = super(Ic50UpdateView, self).get_context_data(**kwargs)
        context["workflow_revision"] = get_object_or_404(get_model("ic50", "IC50WorkflowRevision"), pk=self.workflow_revision_id)
        visualisation_id = self.visualisation_id
        if visualisation_id == 0:
            #This will return the first of the IC50 curves but also generate the others
            context["workflow_revision"].create_ic50_curves()
            visualisation_id = context["workflow_revision"].visualisations.all()[0].id



        context["visualisation_id"] = visualisation_id
        context["visualisation_list"] = context["workflow_revision"].visualisations.all()
        context["visualisation"] = context["visualisation_list"].get(pk=visualisation_id)

        context['revisions'][1][1] = "done"
        context['revisions'][2][1] = "done"
        context['revisions'][0][1] = "done"
        context['revisions'][3][1] = "in-progress"
        context["isic50"] = True

        # if not visualisation_form:
        #     column_data = context["visualisation"].get_column_form_data()
        #     context["visualisation_form"] = VisualisationForm(column_data=column_data, prefix="")
        # else:
        #     context["visualisation_form"] = visualisation_form
        return context


    def get(self, request, *args, **kwargs):
        '''Borrowed from django base detail view'''
        self.workflow_revision_id = kwargs.pop("workflow_revision_id")
        self.visualisation_id = kwargs.pop("visualisation_id")

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


    def post(self, request, *args, **kwargs):

        self.workflow_revision_id = kwargs.pop("workflow_revision_id")
        self.visualisation_id = kwargs.pop("visualisation_id")

        self.object = self.get_object()
        workflow_revision = get_object_or_404(get_model("ic50", "IC50Visualisation"), pk=self.workflow_revision_id)
        visualisation_list = get_model("ic50", "IC50Visualisation").objects.by_workflow_revision(workflow_revision)
        visualisation = visualisation_list.get(pk=self.visualisation_id)
        if request.POST.get("delete", False) == "delete":
            visualisation.delete()
            return HttpResponseRedirect(reverse("visualisation_builder",kwargs={
                'pk': self.object.id,
                'workflow_revision_id' : workflow_revision.id,
                }))
        column_data = visualisation.get_column_form_data()
        vis_update_form = VisualisationForm(request.POST,column_data=column_data )
        if vis_update_form.is_valid():
            new_object = vis_update_form.save(workflow_revision, visualisation=visualisation)
            context = self.get_context_data(object=self.object, visualisation_form=vis_update_form)
            print request.POST
            if request.POST.get("new", False) == "new":
                return HttpResponseRedirect(reverse("visualisation_builder",kwargs={
                'pk': self.object.id,
                'workflow_revision_id' : workflow_revision.id,
                }))
            return self.render_to_response(context)
        else:
            print vis_update_form.errors




class WorkflowHeatmapView(IC50WorkflowDetailView):

    template_name = "workflows/workflow_ic50_heatmap.html"
    workflow_revision_id = None
    workflow_revision = None

    def get(self, request, *args, **kwargs):
        '''Borrowed from django base detail view'''
        self.object = self.get_object()
        self.workflow_revision_id = kwargs.pop("workflow_revision_id")
        self.workflow_revision = self.object.workflow_ic50_revisions.get(pk=self.workflow_revision_id)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(WorkflowHeatmapView, self).get_context_data(**kwargs)
        form_class = HeatmapForm
        #steps_json = json.loads(self.object.get_latest_workflow_revision().steps_json)
        
        steps_json = json.loads(self.workflow_revision.steps_json)

        context["heatmap_form"] = HeatmapForm(uploaded_data=self.workflow_revision.get_data(), steps_json=steps_json)
        context['revisions'][0][1] = "done"
        context['revisions'][1][1] = "in-progress"
        #for testing only
        context['no_next'] = 'disabled'
        context['no_prev'] = 'disabled'
        #these are the real ones
        #context['no_next'] = 'disabled' if workflow_revision.next() == None else ''
        #context['no_prev'] = 'disabled' if workflow_revision.previous() == None else ''

        next_link = '#'
        prev_link = '#'

        context['next_link'] = next_link
        context['prev_link'] = prev_link
        
        
        context.update(kwargs)
        return context

    def post(self, request, *args, **kwargs):
        '''This view will always add a new graph, graph updates are handled by ajax'''
        self.object = self.get_object()
        self.workflow_revision_id = kwargs.pop("workflow_revision_id")
        self.workflow_revision = self.object.workflow_ic50_revisions.get(pk=self.workflow_revision_id)
        steps_json = json.loads(self.workflow_revision.steps_json)
        form = HeatmapForm(request.POST, uploaded_data=self.workflow_revision.get_data(), steps_json=steps_json)
        if form.is_valid():
            #print form.cleaned_data
            steps_json = json.loads(self.workflow_revision.steps_json)
            #form.cleaned_data()
            #loop through the stored json and for each pair, set the value to that in the form data
            #heatmap_json = context["steps_json"]
            for key, value in steps_json.iteritems():
                steps_json[key] = form.cleaned_data[key]

            self.workflow_revision.steps_json = json.dumps(steps_json)
            self.workflow_revision.save()
            self.workflow_revision.create_ic50_data()
            visualisation_id = self.workflow_revision.visualisations.all()[0].id

            return HttpResponseRedirect(
                    reverse('ic50_update_view', kwargs={
                    'pk': self.object.pk,
                    'workflow_revision_id' : self.workflow_revision.id,
                    "visualisation_id" : visualisation_id
                    })
                )