# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0007_auto_20140725_0507'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflowdatamappingrevision',
            name='x_axis',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workflowdatamappingrevision',
            name='y_axis',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='visualisation',
            name='visualisation_type',
            field=models.CharField(max_length=10, choices=[(b'bar', b'Bar Graph'), (b'scatter', b'Scatter Graph'), (b'boxplot', b'Boxplot')]),
        ),
    ]
