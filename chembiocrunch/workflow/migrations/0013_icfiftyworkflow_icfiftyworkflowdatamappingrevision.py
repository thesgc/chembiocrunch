# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workflow', '0012_visualisation_html'),
    ]

    operations = [
        migrations.CreateModel(
            name='IcFiftyWorkflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('title', models.CharField(max_length=100)),
                ('uploaded_config_file', models.FileField(upload_to=b'')),
                ('uploaded_data_file', models.FileField(upload_to=b'')),
                ('created_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': (b'-modified', b'-created'),
                'abstract': False,
                'get_latest_by': b'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IcFiftyWorkflowDataMappingRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('steps_json', models.TextField(default=b'[]')),
                ('revision_type', models.CharField(max_length=5)),
                ('x_axis', models.CharField(max_length=100)),
                ('y_axis', models.CharField(max_length=100)),
                ('workflow', models.ForeignKey(to='workflow.IcFiftyWorkflow')),
            ],
            options={
                'ordering': (b'-modified', b'-created'),
                'abstract': False,
                'get_latest_by': b'modified',
            },
            bases=(models.Model,),
        ),
    ]
