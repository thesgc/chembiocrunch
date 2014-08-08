# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0012_visualisation_html'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visualisation',
            name='split_x_axis_by',
            field=models.CharField(default=None, max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='visualisation',
            name='split_y_axis_by',
            field=models.CharField(default=None, max_length=200, null=True, blank=True),
        ),
    ]
