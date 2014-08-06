# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0010_auto_20140731_0653'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualisation',
            name='error_bars',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
    ]
