# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0007_ic50workflow_archived'),
    ]

    operations = [
        migrations.AddField(
            model_name='ic50workflowrevision',
            name='maximum',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ic50workflowrevision',
            name='maximum_error',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ic50workflowrevision',
            name='minimum',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ic50workflowrevision',
            name='minimum_error',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ic50workflowrevision',
            name='solvent_maximum',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ic50workflowrevision',
            name='solvent_maximum_error',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
    ]
