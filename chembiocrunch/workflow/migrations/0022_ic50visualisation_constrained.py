# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0021_ic50visualisation_results'),
    ]

    operations = [
        migrations.AddField(
            model_name='ic50visualisation',
            name='constrained',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
    ]
