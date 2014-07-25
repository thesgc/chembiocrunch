# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0005_auto_20140723_0319'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visualisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('x_axis', models.CharField(max_length=200)),
                ('y_axis', models.CharField(max_length=200)),
                ('graph_type', models.CharField(max_length=10, choices=[(b'hist', b'Histogram'), (b'bar', b'Bar Graph'), (b'scatter', b'Scatter Graph'), (b'boxplot', b'Boxplot')])),
                ('config_json', models.TextField(default=b'[]')),
                ('data_mapping_revision', models.ForeignKey(to='workflow.WorkflowDataMappingRevision')),
            ],
            options={
                'ordering': (b'-modified', b'-created'),
                'abstract': False,
                'get_latest_by': b'modified',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='workflowdatamappingrevision',
            name='revision_type',
            field=models.CharField(default='', max_length=5),
            preserve_default=False,
        ),
    ]
