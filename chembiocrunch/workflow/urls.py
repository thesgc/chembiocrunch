from django.conf.urls import url
from django.views.generic import TemplateView
from .views import calculations, visualise, workflows

urlpatterns = [
    url(r'^$', workflows.WorkflowListView.as_view() , name='workflow_list'),
    url(r'^create/$', workflows.WorkflowCreateView.as_view(), name='workflow_create'),
    url(r'^create/success/$', TemplateView.as_view(template_name="workflows/workflow_create_success.html"), name='workflow_create_success'),

]