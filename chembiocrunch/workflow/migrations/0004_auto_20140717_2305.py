# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0003_usercolumndatamapping_workflowdatamappingrevisioncolumnlink'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='workflowdatamappingrevisioncolumnlink',
            options={'verbose_name': b'WDCR linked to UCDM'},
        ),
    ]
