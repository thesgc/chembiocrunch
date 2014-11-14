# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0013_auto_20140806_0624'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualisation',
            name='split_by',
            field=models.CharField(default=None, max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='visualisation',
            name='visualisation_type',
            field=models.CharField(max_length=10, choices=[(b'linear_regression', b'Linear Regression'), (b'bar', b'Bar Graph'), (b'scatter', b'Scatter Graph'), (b'point', b'Point Plot')]),
        ),
    ]
