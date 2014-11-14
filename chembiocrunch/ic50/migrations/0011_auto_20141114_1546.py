# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0010_auto_20141113_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ic50visualisation',
            name='data_mapping_revision',
            field=models.ForeignKey(related_name='visualisations', to='ic50.IC50WorkflowRevision'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ic50workflowrevision',
            name='workflow',
            field=models.ForeignKey(related_name='workflow_ic50_revisions', to='ic50.IC50Workflow'),
            preserve_default=True,
        ),
    ]
