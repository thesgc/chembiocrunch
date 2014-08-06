from django.conf.urls import url
from django.views.generic import TemplateView
from .views import calculations, visualise, workflows


urlpatterns = [
    url(r'^$', workflows.WorkflowListView.as_view() , name='workflow_list'),
    url(r'^create/$', workflows.WorkflowCreateView.as_view(), name='workflow_create'),
    url(r'^create-ic50/$', workflows.WorkflowCreateIcFiftyView.as_view(), name='workflow_ic50_create'),
    url(r'^(?P<pk>[0-9]+)/workflow_data_mappings_edit/$', workflows.WorkflowDataMappingEditView.as_view(), name='workflow_data_mappings_edit'),
    url(r'^(?P<pk>[0-9]+)/heatmap/$', workflows.WorkflowHeatmapView.as_view(), name='workflow_ic50_heatmap'),
    url(r'^(?P<pk>[0-9]+)/visualisation_view$', workflows.VisualisationView.as_view(), name='visualisation_view'),
    url(r'^create/success/$', TemplateView.as_view(template_name="workflows/workflow_create_success.html"), name='workflow_create_success'),
   # url(r'^(?P<pk>[0-9]+)/visualisation_export/$', workflows.VisualisationExportView.as_view(), name='visualisation_export'),
    url(r'^(?P<pk>[0-9]+)/visualisation_builder/(?P<workflow_revision_id>[0-9]+)/$', workflows.VisualisationBuilderView.as_view(), name='visualisation_builder'),
    url(r'^(?P<pk>[0-9]+)/visualisation_builder/(?P<workflow_revision_id>[0-9]+)/(?P<visualisation_id>[0-9]+)/$', workflows.VisualisationUpdateView.as_view(), name='visualisation_update_view')

]