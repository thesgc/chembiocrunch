# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0006_auto_20140725_0231'),
    ]

    operations = [
        migrations.RenameField(
            model_name='visualisation',
            old_name='graph_type',
            new_name='visualisation_type',
        ),
    ]
