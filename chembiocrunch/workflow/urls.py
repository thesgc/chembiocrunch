from django.conf.urls import url
from .views import calculations, visualise, workflows

urlpatterns = [
    url(r'^$', workflows.WorkflowListView.as_view() , name='workflow_list'),
    url(r'^create/$', workflows.WorkflowCreateView.as_view(), name='workflow_create'),
    url(r'^(?P<pk>[0-9]+)/workflow_data_mappings_edit/$', workflows.WorkflowDataMappingEditView.as_view(), name='workflow_data_mappings_edit'),
    url(r'^(?P<pk>[0-9]+)/visualisation_view/$', visualise.VisualisationView.as_view(), name='visualisation_view'),
]