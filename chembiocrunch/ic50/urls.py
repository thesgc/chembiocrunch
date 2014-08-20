from django.conf.urls import url
from django.views.generic import TemplateView
from . import views


urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/(?P<workflow_revision_id>[0-9]+)/(?P<visualisation_id>[0-9]+)/$', views.Ic50UpdateView.as_view(), name='ic50_update_view'),
    url(r'^(?P<pk>[0-9]+)/(?P<workflow_revision_id>[0-9]+)/heatmap/$', views.WorkflowHeatmapView.as_view(), name='workflow_ic50_heatmap'),
    url(r'^create-ic50/(?P<form_type>[a-zA-Z0-9]+)$', views.IC50WorkflowCreateView.as_view(), name='workflow_ic50_create'),

]