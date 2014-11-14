from django.forms import widgets
from rest_framework import serializers
from qpcr.models import QPCRWorkflow
from qpcr.fields import JSONField

class QPCRWorkflowSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False,
                                  max_length=300)
    dataset = JSONField()

    class Meta:

        model = QPCRWorkflow