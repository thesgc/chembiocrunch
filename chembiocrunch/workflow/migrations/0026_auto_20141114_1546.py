# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0025_workflow_archived'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visualisation',
            name='data_mapping_revision',
            field=models.ForeignKey(related_name='visualisations', to='workflow.WorkflowDataMappingRevision'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workflowdatamappingrevision',
            name='workflow',
            field=models.ForeignKey(related_name='workflow_data_revisions', to='workflow.Workflow'),
            preserve_default=True,
        ),
    ]
