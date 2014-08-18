# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0022_ic50visualisation_constrained'),
    ]

    operations = [
        migrations.AddField(
            model_name='ic50workflow',
            name='uploaded_meta_file',
            field=models.FileField(default='', max_length=1024, upload_to=b''),
            preserve_default=False,
        ),
    ]
