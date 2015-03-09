# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0013_ic50visualisation_starting_platewell'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ic50visualisation',
            options={'ordering': ['starting_platewell']},
        ),
        migrations.AddField(
            model_name='ic50visualisation',
            name='always_reload',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
