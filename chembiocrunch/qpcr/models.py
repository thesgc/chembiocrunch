from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.conf import settings
from jsonfield import JSONField

# Create your models here.

class QPCRWorkflowManager(models.Manager):
    def get_user_records(self, user):
        groups_list = user.groups.filter(name__in =["affiliation:sgc", "affiliation:tdi"])
        if  groups_list.count() > 0:
            return self.select_related("created_by__groups").filter(created_by__groups__name__in=["affiliation:sgc", "affiliation:tdi"])
        else:
            return self.filter(created_by__id=user.id).select_related("created_by")

    def get_latest_workflow_revision(self, workflow_id):
        return get_model("ic50", "IC50WorkflowRevision").objects.filter(workflow_id=workflow_id, archived=False).order_by("created")[0]



class QPCRWorkflow(TimeStampedModel):
    '''Object to hold the data files for a specific IC50 workflow'''
    title = models.CharField(max_length=300,unique=True)
    dataset = JSONField()
    objects = QPCRWorkflowManager()
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, blank=True, null=True)
    workflow_type = "qpcrworkflow"