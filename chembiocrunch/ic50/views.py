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

from numpy import nan
class IC50WorkflowListView(WorkflowListView):
    '''Lists only the workflows that belong to that user'''
    template_name = "workflows/workflow_list.html"

    def get_queryset(self):
        '''Make sure that all of the views cannot see the object unless they own it!'''
        #need to also pass ic50 models

        return chain(self.model.objects.get_user_records(self.request.user).filter(archived=False), self.ic50_model.objects.get_user_records(self.request.user).filter(archived=False))


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(WorkflowListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books

        context["object_list"] = list(context['object_list'])
        context["FORM_REGISTRY"] = [form_type for form_type in FORM_REGISTRY]
        print context

        return context


    def post(self, request, *args, **kwargs):
        pass















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
        # context['revisions'] = [["upload" ,"not-done"],
        #                         ["validate" ,"not-done"],
        #                         ["visualise", "not-done"],
        #                         ["customise" , "not-done"]]
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

    def get(self, request, *args, **kwargs):
        '''Borrowed from django base detail view'''
        self.object = self.get_object()
        self.workflow_revision_id = kwargs.pop("workflow_revision_id")
        if self.workflow_revision_id == str(0):
            self.workflow_revision = self.object.get_latest_workflow_revision()
            return HttpResponseRedirect(reverse("workflow_ic50_heatmap", kwargs={"pk":self.object.id, "workflow_revision_id":self.workflow_revision.id}))
        else:
            self.workflow_revision = self.object.workflow_ic50_revisions.get(pk=self.workflow_revision_id)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IC50HeatmapView, self).get_context_data(**kwargs)
        form_class = HeatmapForm        
        steps_json = json.loads(self.workflow_revision.steps_json)

        context["heatmap_form"] = HeatmapForm(uploaded_data=self.workflow_revision.get_data(), steps_json=steps_json)

        context["count"] = self.object.workflow_ic50_revisions.all().count()
 
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
        
        context["visualisation_list"] = context["workflow_revision"].visualisations.all()
        context["isic50"] = True

        return context






class Ic50VisualisationView(VisualisationView):
    '''Gets the actual picture for a generated visulisation'''
    model = get_model("ic50", "IC50Visualisation")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.format = kwargs.pop("format")
        self.get_fig()
        if "marked_as_bad_fit" in kwargs:
            if int(kwargs.pop("marked_as_bad_fit")) >0:
                self.object.marked_as_bad_fit = True
            else:
                self.object.marked_as_bad_fit = False
            self.object.save()
            print self.object.marked_as_bad_fit
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

        self.object.save()

    def get_html(self):
        err = self.object.error_class()
        print err
        return JsonResponse({ "html" : add_responsive_tags(self.object.html),
                            "results" : self.object.results ,
                            "error_class" : err})
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

        # if self.format == "ppt":
        #     #create a ppt file
        #     #each slide has one graph
        #     pptx_file_path = '/tmp/test.pptx'
        #     prs = Presentation()
        #     blank_slide_layout = prs.slide_layouts[6]
        #     for vis in vis_list:
        #         slide = prs.slides.add_slide(blank_slide_layout)

        #         #parser = etree.XMLParser(recover=True, encoding='utf-8')
        #         #xml = etree.parse(vis.html, parser)raw_data

        #         #strxml = objectify.dump(xml)

        #         # fig = svg2png(vis.html.encode('utf-8'))
        #         left = Inches(0)
        #         top = Inches(1.5)
        #         pic = slide.shapes.add_picture(fig, left, top)
                
        #     prs.save(file_path)
        #     fsock = open(file_path,"r")
        #     response = HttpResponse(fsock, content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
        #     response['Content-Disposition'] = 'attachment; filename=TestPpt.pptx'
        #     #fc.print_png(response)
        #     return response

        if self.format == "xlsx":
            title = self.object.title + "_output.xlsx"
            path = self.object.get_upload_to("")
            if not os.path.exists(path):
                os.makedirs(path)
            path +="/" +title
            workbook = xlsxwriter.Workbook(path)
            worksheet1 = workbook.add_worksheet()

            meta = self.object.get_meta_data()
            meta = meta.replace(nan, "")
            for index, line in enumerate(meta.to_records()):
                lis = list(line)
                worksheet1.write_row(index,1, lis)


            worksheet = workbook.add_worksheet()
            column_names = ["plate", "coupound_id", "logIC50","ic50 (nM)", "results", "system_comments","user_marked_as_bad_fit", "graph"]
            for i, name in enumerate(column_names):
                worksheet.write(0,i,name)
                if name=="graph":
                    worksheet.set_column(i,i, 140)

            for index, vis in enumerate(vis_list):
                res = json.loads(vis.results).get("values", {})
                worksheet.set_row(index+1, 100)
                worksheet.write(index+1,0,vis.data_mapping_revision.plate_name)
                worksheet.write(index+1,1,vis.compound_id)
                worksheet.write(index+1,2,res.get("logIC50"))
                try:
                   worksheet.write(index+1,3,res.get("IC50"))
                except TypeError:
                    worksheet.write(index+1,3,"N/A")
                worksheet.write(index+1,4,json.dumps(res))
                worksheet.write(index+1,5,res.get("message"))
                if vis.marked_as_bad_fit:
                    worksheet.write(index+1,6,"yes")
                else:
                    worksheet.write(index+1,6,"no")
                if vis.thumb:
                    worksheet.insert_image(index+1,7,vis.thumb.path)
            workbook.close()
            fsock = open(path,"r")
            response = HttpResponse(fsock, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=%s' % title
            #fc.print_png(response)
            return response
