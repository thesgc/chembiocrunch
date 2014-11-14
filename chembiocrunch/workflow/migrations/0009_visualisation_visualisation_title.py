# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0008_auto_20140730_0037'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualisation',
            name='visualisation_title',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
    ]
