from django.shortcuts import render, redirect
from django.views.generic import View,  DetailView, ListView, CreateView
from django.views.generic.detail import SingleObjectMixin

from braces.views import LoginRequiredMixin

from django.db.models import get_model
from .forms import CreateWorkflowForm

class WorkflowView( LoginRequiredMixin):

    model = get_model("workflow", "Workflow")

    def get_queryset(self):
        '''Make sure that all of the views cannot see the object unless they own it!'''
        return self.model.objects.get_user_records(self.request.user)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(WorkflowView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
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

    def form_valid(self, form):
        user = self.request.user
        form.instance.created_by = user
        form_valid = super(WorkflowCreateView, self).form_valid(form)
        print self.object.id


        return form_valid





class WorkflowDetailView( SingleObjectMixin, WorkflowView,):
    pass



class WorkflowOperationChooser(WorkflowDetailView):
    '''Allows the user to choose what to do with their data'''
    def get(self, request, *args, **kwargs):
        return render(request,
            "workflows/workflow_operation_chooser.html")

    def post(self, request, *args, **kwargs):
        pass



