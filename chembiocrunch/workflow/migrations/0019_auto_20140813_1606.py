# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0018_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ic50workflow',
            name='uploaded_config_file',
            field=models.FileField(max_length=1024, upload_to=b''),
        ),
        migrations.AlterField(
            model_name='ic50workflow',
            name='uploaded_data_file',
            field=models.FileField(max_length=1024, upload_to=b''),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='uploaded_file',
            field=models.FileField(max_length=1024, upload_to=b''),
        ),
    ]
