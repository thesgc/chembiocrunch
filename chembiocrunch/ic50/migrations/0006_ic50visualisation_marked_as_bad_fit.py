# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0005_auto_20140901_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='ic50visualisation',
            name='marked_as_bad_fit',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
