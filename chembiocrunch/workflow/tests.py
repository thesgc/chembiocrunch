from __future__ import unicode_literals

from django.test import TestCase, RequestFactory
from workflow.models import Workflow
from django.core.files.base import ContentFile
import random
import string
from django.conf.settings import AUTH_USER_MODEL
from workflow.views import workflows
from django.conf import settings
def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))


class TestWorkflowList(TestCase):

    def workflow_file(self):
        return ContentFile(random_string)

    def setUp(self):
        pass
        # self.u1 = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        # self.u12 = User.objects.create_user('bogus', 'temporary@gmail.com', 'temporary')

        # self.factory = RequestFactory()
        # for i in range(20):
        #     Workflow.objects.create(
        #         title=random_string(), 
        #         uploaded_file=self.workflow_file(),
        #         created_by=self.u1,
        #         )

    def tearDown(self):
        self.u1.delete()
        Workflow.objects.all().delete()


    def test_workflow_index_page_as_creator(self):
        self.client.login(username='temporary', password='temporary')

        # Test my_view() as if it were deployed at /customer/details
        response = self.client.get("/my_workflows/")
        self.assertContains( response, "new row every 12 columns", )


    def test_workflow_index_page_as_other_user(self):
        self.client.login(username='bogus', password='temporary')
        response = self.client.get("/my_workflows/")
        self.assertContains( response, "new row every 12 columns",)




    def test_file_upload(self):
        self.client.login(username='temporary', password='temporary')
        with open(settings.SITE_ROOT + '/workflow/test_data/test_data_1.csv') as fp:
            response = self.client.post('/my_workflows/create/', {'title': 'fred', 'uploaded_file': fp})
        print response.status_code








