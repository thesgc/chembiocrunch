# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ic50workflowrevision',
            name='plate_name',
            field=models.CharField(default=b'', max_length=30),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='ic50workflowrevision',
            name='revision_type',
        ),
    ]
