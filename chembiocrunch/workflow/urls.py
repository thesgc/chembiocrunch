from django.conf.urls import url
from .views import calculations, visualise, workflows

urlpatterns = [
    url(r'^$', workflows.WorkflowListView.as_view() , name='workflow_list'),
    url(r'^create/$', workflows.WorkflowCreateView.as_view(), name='workflow_create'),

]