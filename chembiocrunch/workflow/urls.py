from django.conf.urls import url
from django.views.generic import TemplateView
from . import views


urlpatterns = [
    url(r'^$', views.WorkflowListView.as_view() , name='workflow_list'),
    url(r'^create/$', views.WorkflowCreateView.as_view(), name='workflow_create'),
    url(r'^(?P<pk>[0-9]+)/workflow_data_mappings_edit/$', views.WorkflowDataMappingEditView.as_view(), name='workflow_data_mappings_edit'),

    #url(r'^(?P<pk>[0-9]+)/ic50graphs/$', workflows.IC50VisualisationView.as_view(), name='workflow_ic50_graphs'),
    url(r'^(?P<pk>[0-9]+)/visualisation_view/(?P<format>[a-zA-Z0-9]+)/$', views.VisualisationView.as_view(), name='visualisation_view'),
    url(r'^create/success/$', TemplateView.as_view(template_name="workflows/workflow_create_success.html"), name='workflow_create_success'),
   # url(r'^(?P<pk>[0-9]+)/visualisation_export/$', workflows.VisualisationExportView.as_view(), name='visualisation_export'),
    url(r'^(?P<pk>[0-9]+)/visualisation_builder/(?P<workflow_revision_id>[0-9]+)/$', views.VisualisationBuilderView.as_view(), name='visualisation_builder'),
    url(r'^(?P<pk>[0-9]+)/visualisation_builder/(?P<workflow_revision_id>[0-9]+)/(?P<visualisation_id>[0-9]+)/$', views.VisualisationUpdateView.as_view(), name='visualisation_update_view'),

    url(r'^(?P<pk>[0-9]+)/archive_workflow/', views.VisualisationAjaxArchiveView.as_view(), name='workflow_ajax_archive'),

]