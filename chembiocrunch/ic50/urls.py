from django.conf.urls import url
from django.views.generic import TemplateView
from . import views
from .forms import FORM_REGISTRY
import re
# settings = {
#             'inhib1': {
#                 'cssClass': 'inhib1',
#                 'message': 'Low total inhibition, values could be inaccurate'
#             },
#             'inhib2': {
#                 'cssClass': 'inhib2',
#                 'message': 'No low inhibition range - values could be inaccurate'
#             },
#             'inhib3': {
#                 'cssClass': 'inhib3',
#                 'message': 'Error, no good line fit found'
#             }
#         }

strin = '^create-ic50/(?P<form_type>' + '|'.join(FORM_REGISTRY) + ')$'

urlpatterns = [
    
    url(r'^(?P<pk>[0-9]+)/(?P<workflow_revision_id>[0-9]+)/(?P<visualisation_id>[0-9]+)/$', views.Ic50LoadingAreaAjax.as_view(), name='ic50_loading_area_ajax'),
    url(r'^(?P<pk>[0-9]+)/(?P<workflow_revision_id>[0-9]+)/heatmap/$', views.IC50HeatmapView.as_view(), name='workflow_ic50_heatmap'),
    url(re.compile(strin).pattern, views.IC50WorkflowCreateView.as_view(), name='workflow_ic50_create'),
    url(r'^(?P<pk>[0-9]+)/(?P<workflow_revision_id>[0-9]+)/ajax-graphs/$', views.Ic50ListViewAjax.as_view(), name='ic50_list_view_ajax'),
    url(r'^(?P<pk>[0-9]+)/ic50-export/(?P<format>[a-zA-Z0-9]+)$', views.Ic50ExportAllView.as_view(), name='ic50_export_graphs'),
    url(r'^(?P<pk>[0-9]+)/ic50visualisation_view/(?P<format>[a-zA-Z0-9]+)/$', views.Ic50VisualisationView.as_view(), name='ic50_visualisation_view'),
    #url(r'^(?P<pk>[0-9]+)/ic50visualisation_view/(?P<format>[a-zA-Z0-9]+)/(?P<marked_as_bad_fit>[0-1]+)$', views.Ic50VisualisationView.as_view(), name='ic50_visualisation_update_view'),
    url(r'^(?P<pk>[0-9]+)/ic50visualisation_view/(?P<format>[a-zA-Z0-9]+)/(?P<comment>[a-zA-Z0-9\s%]+)$', views.Ic50VisualisationView.as_view(), name='ic50_visualisation_update_view'),

 ]

# def javascript_settings():
#     return settings;
