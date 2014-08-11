# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0015_merge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='visualisation',
            old_name='split_x_axis_by',
            new_name='split_colour_by',
        ),
        migrations.AlterField(
            model_name='visualisation',
            name='config_json',
            field=models.TextField(default=b'{}'),
        ),
        migrations.AlterField(
            model_name='visualisation',
            name='visualisation_type',
            field=models.CharField(max_length=10, choices=[(b'linear_reg', b'Linear Regression'), (b'bar', b'Bar'), (b'scatter', b'Scatter'), (b'point', b'Point Plot')]),
        ),
    ]
