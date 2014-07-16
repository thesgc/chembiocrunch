from django.db import models

from django_extensions.db.models import TimeStampedModel


class WorkflowManager(models.Manager):
    def get_user_records(self, user):
        return self.filter(created_by=user)

# Create your models here.
class Workflow(TimeStampedModel):
    uploaded_file = models.FileField()
    created_by = models.ForeignKey('auth.User')
    objects = WorkflowManager()
    def data_requires_update(self):
        '''
        method will test if the files attached to the class or the child pages have been updated since the data was last updated
        '''

        last_rev = self.last_data_revision()
        if last_rev == False:
            return True
        data_files_revisied = self.source_data_files.filter(modified__gte=last_rev.modified).count()
        if data_files_revisied > 0:
            return True
        return False


    def last_data_revision(self):
        revisions = WorkflowDataRevision.objects.filter(page_id=self.id).order_by("-modified")
        if revisions.count() > 0:
            return revisions[0]
        return False


    def current_es_client(self):
        '''Only to be used after an index was created by tasks.py'''
        last_revision = self.last_data_revision()
        es_processor = ElasticSearchDataProcessor(self.id, last_revision.id, {})
        return es_processor


    def create_data_revision(self, new_steps_json, label=""):
        '''Generate a workflow revision using the list of steps in the json
        This might be an empty list if this is revision 1 for the particular dataset'''
        return WorkflowDataRevision.objects.create(page=self, steps_json=json.dumps(new_steps_json), label=label)



    @classmethod
    def primary_input_file_fields(cls):
        #for later when we get forms working
        return ["testing1", "testing2"]



class WorkflowDataRevision(TimeStampedModel):
    workflow = models.ForeignKey('Workflow', related_name='workflow_data_revisions')
    label = models.CharField(null=True, default="", blank=True, max_length=200)
    steps_json = models.TextField(default="[]")
