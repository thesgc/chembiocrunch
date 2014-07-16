from django.conf.urls import url
from .views import calculations, visualise, workflows

urlpatterns = [
    url(r'^', workflows.WorkflowListView.as_view()),
    url(r'^/(\w+)/create$', workflows.WorkflowCreateView.as_view()),

]