# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0004_ic50visualisation_raw_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ic50workflow',
            name='title',
            field=models.CharField(max_length=300),
        ),
    ]
