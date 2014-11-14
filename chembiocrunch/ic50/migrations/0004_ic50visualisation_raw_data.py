# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0003_auto_20140829_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='ic50visualisation',
            name='raw_data',
            field=models.TextField(default=b'{}'),
            preserve_default=True,
        ),
    ]
