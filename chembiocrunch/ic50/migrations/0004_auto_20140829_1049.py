# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0004_auto_20140829_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='ic50visualisation',
            name='png',
            field=models.FileField(default=None, null=True, upload_to=b'', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ic50visualisation',
            name='thumb',
            field=models.FileField(default=None, null=True, upload_to=b'', blank=True),
            preserve_default=True,
        ),
    ]
