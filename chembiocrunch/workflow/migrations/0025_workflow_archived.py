# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0024_auto_20140819_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='archived',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
