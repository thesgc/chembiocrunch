# -*- coding: utf8 -*-
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View,  DetailView, ListView, CreateView
from django.views.generic.detail import SingleObjectMixin
from django.conf import settings

from braces.views import LoginRequiredMixin

from django.db.models import get_model
from ic50.forms import  FORM_REGISTRY, HeatmapForm, LabCyteEchoIC50UploadForm
from django.core.urlresolvers import reverse
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset, Reset
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

import matplotlib

import matplotlib.pyplot as plt

import json
from pprint import pprint
import seaborn as sns
from workflow.models import GRAPH_MAPPINGS
from seaborn import plotting_context, set_context
import mpld3
import pandas as pd
from django.forms import Form
from pptx import Presentation
from pptx.util import Inches, Px
import time
from lxml import etree, objectify
from StringIO import StringIO
from datetime import datetime
import os
from workflow.views import VisualisationView, WorkflowListView
from workflow.templatetags.svg_responsive import add_responsive_tags
import xlsxwriter
import time
# Create your views here.
from itertools import chain
from titlecase import titlecase

from numpy import nan

class IC50WorkflowListView(WorkflowListView):
    '''Lists only the workflows that belong to that user'''
    template_name = "workflows/workflow_list.html"

    def get_queryset(self):
        '''Make sure that all of the views cannot see the object unless they own it!'''
        #need to also pass ic50 models
        return self.ic50_model.objects.get_user_records(self.request.user).filter(archived=False)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(WorkflowListView, self).get_context_data(**kwargs)

        context["FORM_REGISTRY"] = [form_type for form_type in FORM_REGISTRY]
        return context

    def post(self, request, *args, **kwargs):
        pass





class IC50WorkflowView(LoginRequiredMixin):
    '''Base class for all views in IC50, will eventually handle permissions'''
    model = get_model("ic50", "IC50Workflow")

    def get_queryset(self):
        '''Make sure that all of the views cannot see the object unless they own it!'''
        return self.model.objects.get_user_records(self.request.user)

    def get_context_data(self, **kwargs):
        '''Adds a status object called revisions to the page context
        which is used to manage breadcrumbs'''
        context = super(IC50WorkflowView, self).get_context_data(**kwargs)
        return context

class IC50WorkflowDetailView(IC50WorkflowView, DetailView, ):
    pass



class IC50WorkflowCreateView(IC50WorkflowView, CreateView ):
    '''creates a single IC50 workflow, saving logic is in forms
    and includes creating a set of revision objects that represent the plates in the 
    IC50 calculation'''
    fields = ['title', 'uploaded_data_file','uploaded_config_file', 'uploaded_meta_file']
    template_name = "workflow_ic50_create.html"
    model = get_model("ic50", "IC50Workflow")
    form_type = None

    def get_form_class(self, **kwargs):
        return FORM_REGISTRY[self.form_type]


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
        # context['revisions'][0][1] = "in-progress"
        context['loggedinuser'] = self.request.user
        return context

    def get_form_kwargs(self):
        kwargs = super(IC50WorkflowCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
 
    def get(self, request, *args, **kwargs):
        self.object = None
        self.form_type = kwargs.pop("form_type")
        return super(IC50WorkflowCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        self.form_type = kwargs.pop("form_type")
        return super(IC50WorkflowCreateView, self).post(request, *args, **kwargs)





 


class Ic50LoadingAreaAjax(IC50WorkflowDetailView):
    '''This view requires refactoring but is used in the 
    ic50 visualisations and updates of ic50 visualisations'''
    pk = None
    workflow_revision_id = None
    visualisation_id = None
    template_name = "visualise/visualisation_builder.html"
    base_html = ""


    def get_context_data(self,  **kwargs):

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

        context["isic50"] = True

        return context


    def get(self, request, *args, **kwargs):
        '''Borrowed from django base detail view'''
        self.workflow_revision_id = kwargs.pop("workflow_revision_id")
        self.visualisation_id = kwargs.pop("visualisation_id")

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)




class IC50HeatmapView(IC50WorkflowDetailView):
    '''Renders a heatmap form for the removal of specific wells from the dataset
    Once the user is happy with a particular dataset they can render it by saving the heatmap'''
    template_name = "workflow_ic50_heatmap.html"
    workflow_revision_id = None
    workflow_revision = None
    index = 1

    def get(self, request, *args, **kwargs):
        '''Borrowed from django base detail view'''
        self.object = self.get_object()
        self.workflow_revision_id = kwargs.pop("workflow_revision_id")
        if self.workflow_revision_id == str(0):
            self.workflow_revision = self.object.get_latest_workflow_revision()
            return HttpResponseRedirect(reverse("workflow_ic50_heatmap", kwargs={"pk":self.object.id, "workflow_revision_id":self.workflow_revision.id}))
        else:
            for ind, wf in enumerate(self.object.workflow_ic50_revisions.all().order_by("created")):
                if int(wf.id) == int(self.workflow_revision_id):
                    self.workflow_revision = wf
                    self.index = ind + 1
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IC50HeatmapView, self).get_context_data(**kwargs)
        form_class = HeatmapForm        
        steps_json = json.loads(self.workflow_revision.steps_json)

        context["heatmap_form"] = HeatmapForm(uploaded_data=self.workflow_revision.get_data(), steps_json=steps_json)
        context["index"] = self.index
        context["count"] = self.object.workflow_ic50_revisions.all().count()
 
        next_qs = self.object.workflow_ic50_revisions.filter(pk__gt=self.workflow_revision.id).order_by("pk")
        if next_qs.count() > 0:
            hm_next = next_qs[0]
        else:
            hm_next = None

        prev_qs = self.object.workflow_ic50_revisions.filter(pk__lt=self.workflow_revision.id).order_by("-pk")
        if prev_qs.count() > 0:
            hm_prev = prev_qs[0]
        else:
            hm_prev = None

        workflow_id = self.workflow_revision.workflow.id

        context['next'] =  hm_next
        context['prev'] =  hm_prev
        context['current'] = self.workflow_revision_id
        context["workflow_revision"] = self.workflow_revision 
        context["vis_count"] = self.workflow_revision.visualisations.all().exclude(html__exact="").count()
        context.update(kwargs)
        return context

    def post(self, request, *args, **kwargs):
        '''This view will render the second half of the page of graphs'''
        self.object = self.get_object()
        self.workflow_revision_id = kwargs.pop("workflow_revision_id")
        self.workflow_revision = self.object.workflow_ic50_revisions.get(pk=self.workflow_revision_id)
        steps_json = json.loads(self.workflow_revision.steps_json)
        form = HeatmapForm(request.POST, uploaded_data=self.workflow_revision.get_data(), steps_json=steps_json)
        if form.is_valid():
            steps_json = json.loads(self.workflow_revision.steps_json)
            steps_json.update(form.cleaned_data)

            deactivated = [key for key, value in steps_json.iteritems() if not value]
            config_columns = self.workflow_revision.get_config_data()
            inactive = config_columns[config_columns["full_ref"].isin(deactivated)]
            inactive["status"] = "inactive"
            config_columns.update(inactive)
            config_columns.to_hdf(self.workflow_revision.get_store_filename("configdata"),self.workflow_revision.get_store_key(), mode='w')
            
            vis_list = get_model("ic50", "ic50visualisation").objects.filter(data_mapping_revision__id=self.workflow_revision.id)
            ic50_groups = config_columns.groupby("global_compound_id")
            for vis in vis_list:

                group_df = ic50_groups.get_group(vis.compound_id)
                #Here we rebuild a given vis if some of its points have been excluded
                if len(group_df[group_df["status"].isin(["inactive",])]) != 0:
                    vis.raw_data = group_df.to_json()
                    vis.html = ""
                    vis.save()

            self.workflow_revision = self.object.workflow_ic50_revisions.get(pk=self.workflow_revision_id)
            self.workflow_revision.steps_json = json.dumps(steps_json)
            self.workflow_revision.save()


            #for the ajax graph loading, we can't redirect and we (I) can't send back a rendered view 
            #send back necessary config data to generate graphs
            if request.is_ajax():
                return JsonResponse({'pk': self.object.pk, 'workflow_revision_id' : self.workflow_revision.id,  })

            #this needs to render to response rather than redirect
            return HttpResponseRedirect(
                    reverse('ic50_loading_area_ajax', kwargs={
                    'pk': self.object.pk,
                    'workflow_revision_id' : self.workflow_revision.id,
                    "visualisation_id" : visualisation_id,
                    "base_html" : "workflow_base.html"
                    })
                )
            

class Ic50ListViewAjax(IC50WorkflowDetailView):
    '''Class to fetch ic50 curves via ajax that is called by the Ic50LoadingAreaAjax'''
    workflow_revision_id = None
    visualisation_id = None
    template_name= "ic50_visualisation_list_ajax.html"

    def get(self, request, **kwargs):
        self.workflow_revision_id = kwargs.pop("workflow_revision_id")
        self.visualisation_id = kwargs.pop("pk")
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


    def get_context_data(self,  **kwargs):

        context = super(Ic50ListViewAjax, self).get_context_data(**kwargs)
        context["workflow_revision"] = get_object_or_404(get_model("ic50", "IC50WorkflowRevision"), pk=self.workflow_revision_id)
        visualisation_id = self.visualisation_id
        if visualisation_id == 0:
            #This will return the first of the IC50 curves but also generate the others
            context["workflow_revision"].create_ic50_curves()
            visualisation_id = context["workflow_revision"].visualisations.all()[0].id

        context["visualisation_id"] = visualisation_id
        
        context["visualisation_list"] = context["workflow_revision"].visualisations.all().order_by("created")
        context["isic50"] = True

        return context






class Ic50VisualisationView(VisualisationView):
    '''Gets the actual picture for a generated visulisation'''
    model = get_model("ic50", "IC50Visualisation")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.format = kwargs.pop("format")
        self.get_fig()
        if "comment" in kwargs:
            self.object.comment = kwargs.pop("comment")
            self.object.save()
        self.object = self.get_object()
        if self.format=="html":
            return self.get_html()
        if self.format=="png":
            return self.get_png()



    def get_fig(self):
        curve_fitter = self.object.get_curve_fitter()
        path = (self.object.get_upload_to(""))
        if not os.path.exists(path):
            os.makedirs(path)
        pngfile = path + "large.png"
        thumbfile = path + "thumb.png"
        curve_fitter.get_fig(labels=True, pngfile=str(pngfile), thumbfile=str(thumbfile))
        self.object.png = pngfile
        self.object.thumb = thumbfile

        self.object.html = curve_fitter.svg
        self.object.results = json.dumps({"values": curve_fitter.results})
        self.object.comment = curve_fitter.results.get("message", self.object.GOOD_CURVE)

        self.object.save()

    def get_html(self):
        err = self.object.error_class()
        return JsonResponse({ "html" : add_responsive_tags(self.object.html),
                            "results" : self.object.results ,
                            "error_class" : err,
                            "comment" : self.object.comment})
    def get_png(self):
        fsock = open(self.object.png.path,"r")
        response = HttpResponse(fsock, content_type='image/png')
        response['Content-Disposition'] = 'attachment; filename="%s.png"'% self.object.compound_id
        return response








class Ic50ExportAllView(IC50WorkflowDetailView):
    #pull out what sort of visualisation to generate
    #base on VisualisationView - create a slide/image etc
    format = None
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.format = kwargs.pop("format")
        context = self.get_context_data(object=self.object)
        vis_list = get_model("ic50", "ic50visualisation").objects.filter(data_mapping_revision__workflow__id=self.object.id)

        if self.format == "xlsx":
            title = self.object.title + "_output.xlsx"
            path = self.object.get_upload_to("")
            if not os.path.exists(path):
                os.makedirs(path)
            path +="/" +title
            workbook = xlsxwriter.Workbook(path)
            worksheet1 = workbook.add_worksheet("Assay Meta Data")
            bold = workbook.add_format({'bold': True})

            meta = self.object.get_meta_data()
            meta = meta.replace(nan, "")
            worksheet1.set_column(0,10, 40)

            for index, line in enumerate(meta.to_records()):
                lis = list(line)[1:]
                worksheet1.write_row(index,0, lis)


            worksheet = workbook.add_worksheet("Results Summary")
            column_names = [u"Plate", u"Compound id", u"LogIC50",u"IC50 (μM)", u"IC50 standard error", "Hill", "Hill standard error", "System Comments", "graph"]
            for i, name in enumerate(column_names):
                worksheet.write(0,i,name, bold)
                worksheet.set_column(i,i, 20)

            for index, vis in enumerate(vis_list):
                res = json.loads(vis.results).get("values", {})
                worksheet.set_row(index+1, 100)
                worksheet.write(index+1,0,vis.data_mapping_revision.plate_name)
                worksheet.write(index+1,1,vis.compound_id)
                worksheet.write(index+1,2,res.get("logIC50"))
                try:
                    worksheet.write(index+1,3,res.get("IC50"))
                    worksheet.write(index+1,4,res.get("IC50error"))
                    worksheet.write(index+1,5,res.get("hill"))
                    worksheet.write(index+1,6,res.get("hillerror"))

                except TypeError:
                    worksheet.write(index+1,3,"N/A")
                    worksheet.write(index+1,4,res.get("N/A"))
                    worksheet.write(index+1,5,"N/A")
                    worksheet.write(index+1,6,res.get("N/A"))
                worksheet.write(index+1,7,res.get("message"))
                if vis.thumb:
                    worksheet.insert_image(index+1,8,vis.thumb.path)
            

            index =0
            username = self.object.get_username_for_export()
            worksheet2 = workbook.add_worksheet("Results Beehive Format")
            for index, vis in enumerate(vis_list):
                res = json.loads(vis.results).get("values", {})
                logic50 = res.get("logIC50", "N/A")
                if logic50 != "N/A":
                    logic50 = logic50 -6

                logic50error = res.get("logIC50error","N/A")
                if logic50error != "N/A":
                    logic50error = logic50error -6

                row_data = [(u"  Experiment Type (Alphascreen) ", self.object.meta_by_name("Assay Type") ,),
                    (u"  Purification ID (Purification) ", self.object.meta_by_name("Protein") ,),
                    (u"  Protein Concentration (uM) (Alphascreen) ", self.object.meta_by_name("Protein Concentration (nM)") ,), #Issue with units
                    (u"  SGC Global Compound ID (Batch) (Peptide) ", self.object.meta_by_name("Peptide ID") ,),
                    (u"  SGC Global Compound ID (Batch) (Compound) ", vis.compound_id ,),
                    (u"  Peptide Concentration (uM) (Alphascreen) ", self.object.meta_by_name("Peptide Concentration (nM)") ,),
                    (u"  Solvent (Alphascreen) ", self.object.meta_by_name("Solvent"),),
                    (u"  Solvent Concentration (%) (Alphascreen) ", self.object.meta_by_name("Solvent Concentration") ,),
                    (u"  Buffer (Alphascreen) ", self.object.meta_by_name("Assay Buffer") ,),
                    (u"  Compound Incubation Time (mins) (Alphascreen) ", self.object.meta_by_name("Compound Incubation Time (mins)") ,),
                    (u"  Peptide Incubation Time (mins) (Alphascreen) ", self.object.meta_by_name("Peptide Incubation Time") ,),
                    (u"  Bead Incubation Time (mins) (Alphascreen) ", self.object.meta_by_name("Bead Incubation Time") ,),
                    (u"  Incubation Temperatures (C) (Alphascreen) ", self.object.meta_by_name("Incubation Temperature") ,),
                    (u"  LogIC50 (relative to 1M) (Data Summary) ", logic50 ,),
                    (u"  LogIC50 error (Data Summary) ",logic50error ,),
                    (u"  IC50 (Data Summary) ", res.get("IC50", "") ,),
                    (u"  Curve Fit: Upper 95% ConfLimit (Data Summary) ", res.get("IC50_upper_95", "") ,),
                    (u"  Curve Fit: Lower 95% ConfLimit (Data Summary) ", res.get("IC50_lower_95", ""),),
                    (u"  Curve Fit: Hill Slope (Data Summary) ", res.get("IC50_lower_95", "") ,),
                    (u"  Curve (Obsolete) (Data Summary) ", "" ,),
                    (u"  Curve Fit: Bottom (Data Summary) ", res.get("bottom", "") ,),
                    (u"  Curve Fit: Top (Data Summary) ", res.get("top", "") ,),
                    (u"  R2 (Data Summary) ", res.get("r-squared", "") ,),
                    (u"  Data Quality (Data Summary) ", "" ,),
                    (u"  Comments on Curve Fit (Data Summary) ", "" ,),
                    (u"  Enzyme Reference (Alphascreen) ", vis.data_mapping_revision.maximum ,),
                    (u"  Enzyme Reference Error (Alphascreen) ", vis.data_mapping_revision.maximum_error ,),]
                
                conc_generator = vis.get_results_for_datapoint()
                for datum in conc_generator:
                    row_data += datum

                row_data +=   [(u"  No Protein Control Activity (Alphascreen) ", vis.data_mapping_revision.minimum ,),
                    (u"  No Protein Control Error (Alphascreen) ", vis.data_mapping_revision.minimum_error ,),
                    (u"  No Peptide Control Activity (Alphascreen) ", "" ,),
                    (u"  No Peptide Control Error (Alphascreen) ", "" ,),
                    (u"  Solvent Control 1 Inhibition (%) (Solvent Controls) ", vis.data_mapping_revision.solvent_maximum ,),
                    (u"  Solvent Control 1 Inhibition Error (%) (Solvent Controls) ", vis.data_mapping_revision.solvent_maximum_error ,),
                    (u"  Solvent Control 2 Inhibition (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 2 Inhibition Error (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 3 Inhibition (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 3 Inhibition Error (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 4 Inhibition (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 4 Inhibition Error (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 5 Inhibition (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 5 Inhibition Error (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 6 Inhibition (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 6 Inhibition Error (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 7 Inhibition (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 7 Inhibition Error (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 8 Inhibition (%) (Solvent Controls) ", "" ,),
                    (u"  Solvent Control 8 Inhibition Error (%) (Solvent Controls) ", "" ,),
                    (u"  Compound Concentration 1 Counter Screen Inhibition (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 1 Counter Screen Inhibition Error (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 2 Counter Screen Inhibition (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 2 Counter Screen Inhibition Error (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 3 Counter Screen Inhibition (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 3 Counter Screen Inhibition Error (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 4 Counter Screen Inhibition (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 4 Counter Screen Inhibition Error (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 5 Counter Screen Inhibition (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 5 Counter Screen Inhibition Error (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 6 Counter Screen Inhibition (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 6 Counter Screen Inhibition Error (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 7 Counter Screen Inhibition (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 7 Counter Screen Inhibition Error (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 8 Counter Screen Inhibition (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  Compound Concentration 8 Counter Screen Inhibition Error (%) (Counter Screen Inhibition) ", "" ,),
                    (u"  ELN ID (Alphascreen) ", self.object.meta_by_name("ELN Ref") ,),
                    (u"  Comments (Alphascreen) ", vis.comment ,),
                    (u"  Date record created (Alphascreen) ", self.object.meta_by_name("Date of Assay") ,),
                    (u"  Creator of record (Alphascreen) ", username ,)]
                if index == 0:
                    worksheet2.write_row(0,0,[item[0] for item in row_data], bold)#

                worksheet2.write_row(index+1,0,["N/A" if (str(item[1]).lower() == "nan") else "N/A" if (str(item[1]).lower() == "inf") else item[1] for item in row_data])

            workbook.close()
            fsock = open(path,"r")
            response = HttpResponse(fsock, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=%s' % title
            return response
