# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0011_auto_20141114_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ic50visualisation',
            name='png',
            field=models.FileField(default=None, max_length=1000, null=True, upload_to=b'', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ic50visualisation',
            name='thumb',
            field=models.FileField(default=None, max_length=1000, null=True, upload_to=b'', blank=True),
            preserve_default=True,
        ),
    ]
