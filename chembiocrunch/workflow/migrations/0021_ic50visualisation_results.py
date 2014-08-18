# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0020_ic50visualisation'),
    ]

    operations = [
        migrations.AddField(
            model_name='ic50visualisation',
            name='results',
            field=models.TextField(default=b'{}'),
            preserve_default=True,
        ),
    ]
