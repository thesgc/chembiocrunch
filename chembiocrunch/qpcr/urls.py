from django.conf.urls import patterns, url
from qpcr import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^workflows/$', csrf_exempt(views.workflow_list)),
    url(r'^workflows/(?P<id>[0-9]+)$', csrf_exempt(views.workflow_detail)),
]