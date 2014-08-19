# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0023_ic50workflow_uploaded_meta_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ic50visualisation',
            name='data_mapping_revision',
        ),
        migrations.DeleteModel(
            name='IC50Visualisation',
        ),
        migrations.RemoveField(
            model_name='ic50workflow',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='ic50workflowrevision',
            name='workflow',
        ),
        migrations.DeleteModel(
            name='IC50Workflow',
        ),
        migrations.DeleteModel(
            name='IC50WorkflowRevision',
        ),
    ]
