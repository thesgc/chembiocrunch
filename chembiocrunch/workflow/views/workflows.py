from django.shortcuts import render, redirect
from django.views.generic import View,  DetailView, ListView, CreateView
from django.views.generic.detail import SingleObjectMixin

from braces.views import LoginRequiredMixin

from django.db.models import get_model
from workflow.forms import CreateWorkflowForm, DataMappingForm, DataMappingFormSetHelper, DataMappingFormSet, ResetButton
from django.core.urlresolvers import reverse
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field, Fieldset, Reset
from django.http import HttpResponseRedirect, HttpResponse
import seaborn as sns
import matplotlib.pyplot as plt

from django.shortcuts import render, redirect
from django.views.generic import View,  DetailView, ListView, CreateView
from django.views.generic.detail import SingleObjectMixin

from braces.views import LoginRequiredMixin

from django.db.models import get_model

from django.http import HttpResponseRedirect, HttpResponse

from workflow.models import GRAPH_MAPPINGS
from workflow.forms import VisualisationForm
from seaborn import plotting_context, set_context
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

class WorkflowView( LoginRequiredMixin):

    model = get_model("workflow", "Workflow")

    def get_queryset(self):
        '''Make sure that all of the views cannot see the object unless they own it!'''
        return self.model.objects.get_user_records(self.request.user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(WorkflowView, self).get_context_data(**kwargs)
        context['revisions'] = [["upload" ,"not-done"],
                                ["validate" ,"not-done"],
                                ["visualise", "not-done"],
                                ["cleanse" , "not-done"]]
        return context


class WorkflowListView(WorkflowView, ListView):
    '''Lists only the workflows that belong to that user'''
    template_name = "workflows/workflow_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(WorkflowListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books

        context["object_list"] = list(context['object_list'])

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

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(WorkflowCreateView, self).get_context_data(**kwargs)
        context['revisions'][0][1] = "in-progress"
        return context


prefix="data_mappings"



class WorkflowDetailView(WorkflowView, DetailView, ):
    pass



class WorkflowOperationChooser(WorkflowDetailView):
    '''Allows the user to choose what to do with their data'''
    def get(self, request, *args, **kwargs):
        return render(request,
            "workflows/workflow_operation_chooser.html")

    def post(self, request, *args, **kwargs):
        pass


def vis_label_filter_prexix(vis_id):
    return "vis_label_filter_%d" % vis_id

def vis_option_prexix(vis_id):
    return "vis_options_%d" % vis_id

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
            context["formset"] = DataMappingFormSet(initial=self.object.get_data_mapping_formset_data(), prefix="data_mappings")
        context.update(kwargs)
        helper = DataMappingFormSetHelper()
        helper.template = 'table_inline.html'
        for mapping in GRAPH_MAPPINGS:
            helper.add_input(Submit(mapping, GRAPH_MAPPINGS[mapping]["name"]))

        helper.add_input(Submit("other", "Other"))
        helper.add_input(ResetButton("reset", "Reset Form"))

        context["helper"] = helper
        visualisations = get_model("workflow","visualisation").objects.by_workflow(self.object)
        vis_dicts = []
        for vis in visualisations:
            initial_data = vis.get_initial_form_data()
            column_data = vis.get_column_form_data()
            print column_data
            vis_dict = vis.__dict__
            vis_dict["vis_option_form"] = VisualisationForm(initial=initial_data, prefix=vis_option_prexix(vis.id), column_data=column_data)
            vis_dicts.append(vis_dict)
        context["visualisations"] = vis_dicts

        if visualisations.count() > 0:
            context['revisions'][1][1] = "in-progress"
            context['revisions'][2][1] = "done"
        else:
            context['revisions'][1][1] = "in-progress"
        context['revisions'][2][1] = "done"
        return context

    def post(self, request, *args, **kwargs):
        '''This view will always add a new graph, graph updates are handled by ajax'''
        self.object = self.get_object()
        formset = DataMappingFormSet(request.POST, prefix="data_mappings")
        if formset.is_valid():
            data_changed = False
            for form in formset:
                if "dtype" in form.changed_data or "name" in form.changed_data:
                    data_changed = True
            if data_changed == True:
                steps_json = [{"cleaned_data" : form.cleaned_data, "changed_data" : form.changed_data }  for form in formset]
                workflow_revision = self.object.validate_columns(steps_json)
            else:
                workflow_revision = self.object.get_latest_data_revision()

            for mapping in GRAPH_MAPPINGS:
                if mapping in formset.data:
                    new_visualisation = get_model("workflow","Visualisation").objects.create(
                                                                    visualisation_type=mapping, 
                                                                    x_axis=formset.get_column_name_from_boolean("use_as_x_axis"),
                                                                    y_axis=formset.get_column_name_from_boolean("use_as_y_axis"), 
                                                                    data_mapping_revision=workflow_revision,
                                                                    )



            return self.render_to_response(self.get_context_data(formset=formset,))
        return self.render_to_response(self.get_context_data(formset=formset))





class VisualisationView(DetailView):
    model = get_model("workflow", "visualisation")

    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get a context
    #     context = super(VisualisationView, self).get_context_data(**kwargs)
    #     if not "form" in kwargs:
    #         form = PlotForm()
    #     else:
    #         form= kwargs.get("form")
    #     context["form"] = form
    #     return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        df = self.object.data_mapping_revision.get_data()

        with plotting_context( "talk" ):

            g = sns.FacetGrid(df, size=10, aspect=2)
            #g.map(GRAPH_MAPPINGS[self.object.graph_type]["function"], self.object.x_axis, self.object.y_axis);
            g.map(GRAPH_MAPPINGS["bar"]["function"], self.object.x_axis, self.object.y_axis)
            plt.plot()
            fc = FigureCanvas(plt.figure(1))
            response = HttpResponse(content_type='image/png')
            fc.print_png(response)
            return response




