from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

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


urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/(?P<workflow_revision_id>[0-9]+)/(?P<visualisation_id>[0-9]+)/$', views.Ic50UpdateView.as_view(), name='ic50_update_view'),
    url(r'^(?P<pk>[0-9]+)/heatmap/$', views.WorkflowHeatmapView.as_view(), name='workflow_ic50_heatmap'),
    url(r'^create-ic50/(?P<form_type>[a-zA-Z0-9]+)$', views.IC50WorkflowCreateView.as_view(), name='workflow_ic50_create'),

 ]

# def javascript_settings():
#     return settings;