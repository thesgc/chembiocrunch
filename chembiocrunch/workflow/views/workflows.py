from django.shortcuts import render, redirect
from django.views.generic import View,  DetailView, ListView, CreateView
from django.views.generic.detail import SingleObjectMixin

from braces.views import LoginRequiredMixin

from django.db.models import get_model


class WorkflowView( LoginRequiredMixin):

    model = get_model("workflow", "Workflow")

    def get_queryset(self, request):
        '''Make sure that all of the views cannot see the object unless they own it!'''
        return Workflow.objects.get_user_records(self, request.user)




class WorkflowListView(ListView, WorkflowView):
    '''Lists only the workflows that belong to that user'''
    def get(self, request, *args, **kwargs):
        return render(request,
            "workflows/workflow_list.html")

    def post(self, request, *args, **kwargs):
        pass


class WorkflowCreateView(CreateView, WorkflowView):
    '''Renders or creates a single workflow'''
    def get(self, request, *args, **kwargs):
        return render(request,
            "workflows/workflow_create.html")

    def post(self, request, *args, **kwargs):
        pass





class WorkflowDetailView( SingleObjectMixin, WorkflowView,):
    pass



class WorkflowOperationChooser(WorkflowDetailView):
    '''Allows the user to choose what to do with their data'''
    def get(self, request, *args, **kwargs):
        return render(request,
            "workflows/workflow_operation_chooser.html")

    def post(self, request, *args, **kwargs):
        pass



