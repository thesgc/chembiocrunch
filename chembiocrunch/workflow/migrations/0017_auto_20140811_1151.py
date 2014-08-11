# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0016_auto_20140808_0743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visualisation',
            name='visualisation_type',
            field=models.CharField(max_length=10, choices=[(b'linear_reg', b'Linear Regression'), (b'bar', b'Bar'), (b'scatter', b'Scatter'), (b'point', b'Point Plot')]),
        ),
    ]
