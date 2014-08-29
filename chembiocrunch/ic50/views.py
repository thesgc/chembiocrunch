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
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

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
import time
from cairosvg import svg2png
from lxml import etree, objectify
from StringIO import StringIO
from datetime import datetime
from ic50.curve_fit import IC50CurveFit

from workflow.views import VisualisationView

# Create your views here.
class IC50WorkflowView(LoginRequiredMixin):
    '''Base class for all views in IC50, will eventually handle permissions'''
    model = get_model("ic50", "IC50Workflow")

    # def get_queryset(self):
    #     '''Make sure that all of the views cannot see the object unless they own it!'''
    #     return self.model.objects.get_user_records(self.request.user)

    def get_context_data(self, **kwargs):
        '''Adds a status object called revisions to the page context
        which is used to manage breadcrumbs'''
        context = super(IC50WorkflowView, self).get_context_data(**kwargs)
        context['revisions'] = [["upload" ,"not-done"],
                                ["validate" ,"not-done"],
                                ["visualise", "not-done"],
                                ["customise" , "not-done"]]
        return context

class IC50WorkflowDetailView(IC50WorkflowView, DetailView, ):
    pass

class IC50WorkflowCreateView(IC50WorkflowView, CreateView ):
    '''creates a single IC50 workflow, saving logic is in forms
    and includes creating a set of revision objects that represent the plates in the 
    IC50 calculation'''
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
    '''This view requires refactoring but is used in the 
    ic50 visualisations and updates of ic50 visualisations'''
    pk = None
    workflow_revision_id = None
    visualisation_id = None
    template_name = "visualise/visualisation_builder.html"
    base_html = ""

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


        context["base_html"] = self.base_html
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
            if request.POST.get("new", False) == "new":
                return HttpResponseRedirect(reverse("visualisation_builder",kwargs={
                'pk': self.object.id,
                'workflow_revision_id' : workflow_revision.id,
                }))
            return self.render_to_response(context)
        else:
            pass
            #print vis_update_form.errors




class WorkflowHeatmapView(IC50WorkflowDetailView):
    '''Renders a heatmap form for the removal of specific wells from the dataset
    Once the user is happy with a particular dataset they can render it by saving the heatmap'''
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

         
        next_qs = self.object.workflow_ic50_revisions.filter(pk__gt=self.workflow_revision.id).order_by("pk")
        if next_qs.count() > 0:
            hm_next = next_qs[0]
        else:
            hm_next = None

        prev_qs = self.object.workflow_ic50_revisions.filter(pk__lt=self.workflow_revision.id).order_by("pk")
        if prev_qs.count() > 0:
            hm_prev = prev_qs[0]
        else:
            hm_prev = None

        workflow_id = self.workflow_revision.workflow.id

        context['next'] =  hm_next
        context['prev'] =  hm_prev
        context['current'] = self.workflow_revision_id
        
        
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
            steps_json = json.loads(self.workflow_revision.steps_json)
            
            for key, value in steps_json.iteritems():
                steps_json[key] = form.cleaned_data[key]

            self.workflow_revision.steps_json = json.dumps(steps_json)
            self.workflow_revision.save()
            #TODO we should check first that there are graphs to generate? Or should the generate process replace existing graphs?
            #if visualisation_id == 0:
            #    self.workflow_revision.create_ic50_data()
            #self.workflow_revision.create_ic50_data()
            visualisation_id = self.workflow_revision.visualisations.all()[0].id

            #for the ajax graph loading, we can't redirect and we (I) can't send back a rendered view 
            #send back necessary config data to generate graphs
            if request.is_ajax():
                return JsonResponse({'pk': self.object.pk, 'workflow_revision_id' : self.workflow_revision.id, "visualisation_id" : visualisation_id, })

            #this needs to render to response rather than redirect
            return HttpResponseRedirect(
                    reverse('ic50_update_view', kwargs={
                    'pk': self.object.pk,
                    'workflow_revision_id' : self.workflow_revision.id,
                    "visualisation_id" : visualisation_id,
                    "base_html" : "workflow_base.html"
                    })
                )
            

class Ic50AjaxGraphs(IC50WorkflowDetailView):
    '''Class to fetch ic50 curves via ajax for the existing sideloading heatmap page'''
    workflow_revision_id = None
    visualisation_id = None
    template_name= "visualise/visualisation_list_ajax.html"

    def get(self, request, **kwargs):
        self.workflow_revision_id = kwargs.pop("workflow_revision_id")
        self.visualisation_id = kwargs.pop("pk")
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self,  **kwargs):
        # visualisation_form = None
        # if "visualisation_form" in kwargs:
        #     visualisation_form = kwargs.pop("visualisation_form")

        context = super(Ic50AjaxGraphs, self).get_context_data(**kwargs)
        context["workflow_revision"] = get_object_or_404(get_model("ic50", "IC50WorkflowRevision"), pk=self.workflow_revision_id)
        visualisation_id = self.visualisation_id
        if visualisation_id == 0:
            #This will return the first of the IC50 curves but also generate the others
            context["workflow_revision"].create_ic50_curves()
            visualisation_id = context["workflow_revision"].visualisations.all()[0].id

        context["visualisation_id"] = visualisation_id
        
        context["visualisation_list"] = context["workflow_revision"].visualisations.all()
        #context["visualisation_list"] = vis_groupings

        #context["visualisation"] = context["visualisation_list"].get(pk=visualisation_id)

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






class Ic50VisualisationView(VisualisationView):
    model = get_model("ic50", "IC50Visualisation")

    def get_fig(self):
        ic50_group = self.object.compound_id
        configdata = self.object.data_mapping_revision.get_config_data()
        group_df = configdata[configdata["global_compound_id"].isin([ic50_group,])]
        group_df.sort(["percent_inhib","concentration"], inplace=True)
        curve_fitter = IC50CurveFit(main_group_df=group_df)
        title = "%s" % ic50_group
        fit = curve_fitter.get_fit(constrained=True)
        curve_fitter.get_fig(labels=False)
        self.fig = curve_fitter.fig       
        curve_fitter.get_fig(labels=True)
        self.object.html = curve_fitter.svg
        self.object.results = json.dumps(curve_fitter.results)
        self.object.save()













class Ic50ExportAllView(IC50WorkflowDetailView):
    #pull out what sort of visualisation to generate
    #base on VisualisationView - create a slide/image etc
    model = get_model("ic50", "ic50visualisation")
    format = None
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.format = kwargs.pop("format")
        self.workflow_revision_id = kwargs.pop("workflow_revision_id")
        context = self.get_context_data(object=self.object)
        context["workflow_revision"] = get_object_or_404(get_model("ic50", "IC50WorkflowRevision"), pk=self.workflow_revision_id)
        vis_list = context["workflow_revision"].visualisations.all()

        if self.format == "ppt":
            #create a ppt file
            #each slide has one graph
            pptx_file_path = '/tmp/test.pptx'
            prs = Presentation()
            blank_slide_layout = prs.slide_layouts[6]
            for vis in vis_list:
                slide = prs.slides.add_slide(blank_slide_layout)

                #parser = etree.XMLParser(recover=True, encoding='utf-8')
                #xml = etree.parse(vis.html, parser)

                #strxml = objectify.dump(xml)

                # fig = svg2png(vis.html.encode('utf-8'))
                left = Inches(0)
                top = Inches(1.5)
                pic = slide.shapes.add_picture(fig, left, top)
                
            prs.save(file_path)
            fsock = open(file_path,"r")
            response = HttpResponse(fsock, content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            response['Content-Disposition'] = 'attachment; filename=TestPpt.pptx'
            #fc.print_png(response)
            return response




        # fig = self.object.get_fig_for_dataframe()
        # self.fc = matplotlib.backends.backend_agg.FigureCanvasAgg(fig)
        # if self.format=="png":
        #     return self.get_png()
        # if self.format=="svg":
        #     return self.get_svg()
        # if self.format=="ppt":
        #     return self.get_ppt()
