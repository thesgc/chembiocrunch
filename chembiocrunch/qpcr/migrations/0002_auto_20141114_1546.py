# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('qpcr', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qpcrworkflow',
            name='created_by',
            field=models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='qpcrworkflow',
            name='dataset',
            field=jsonfield.fields.JSONField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='qpcrworkflow',
            name='title',
            field=models.CharField(unique=True, max_length=300),
            preserve_default=True,
        ),
    ]
