# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0006_ic50visualisation_marked_as_bad_fit'),
    ]

    operations = [
        migrations.AddField(
            model_name='ic50workflow',
            name='archived',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
