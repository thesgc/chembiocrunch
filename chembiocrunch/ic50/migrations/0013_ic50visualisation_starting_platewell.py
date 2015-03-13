# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0012_auto_20150309_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='ic50visualisation',
            name='starting_platewell',
            field=models.CharField(default=b'', max_length=10, null=True, blank=True),
            preserve_default=True,
        ),
    ]
