# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0011_visualisation_error_bars'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualisation',
            name='html',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
