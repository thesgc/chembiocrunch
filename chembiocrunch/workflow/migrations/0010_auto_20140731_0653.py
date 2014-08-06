# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0009_visualisation_visualisation_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualisation',
            name='split_x_axis_by',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='visualisation',
            name='split_y_axis_by',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
    ]
