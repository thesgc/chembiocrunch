# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0004_auto_20140717_2305'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usercolumndatamapping',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='workflowdatacolumnsrevision',
            name='schema_revision',
        ),
        migrations.RemoveField(
            model_name='workflowdatamappingrevisioncolumnlink',
            name='user_column_data_mapping',
        ),
        migrations.DeleteModel(
            name='UserColumnDataMapping',
        ),
        migrations.RemoveField(
            model_name='workflowdatamappingrevisioncolumnlink',
            name='workflow_data_column_revision',
        ),
        migrations.DeleteModel(
            name='WorkflowDataColumnsRevision',
        ),
        migrations.DeleteModel(
            name='WorkflowDataMappingRevisionColumnLink',
        ),
    ]
