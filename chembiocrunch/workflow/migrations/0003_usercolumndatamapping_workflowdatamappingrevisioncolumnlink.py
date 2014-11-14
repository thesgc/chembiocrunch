# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('workflow', '0002_auto_20140717_0224'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserColumnDataMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('name', models.CharField(max_length=250)),
                ('slug', models.CharField(max_length=250)),
                ('data_type', models.CharField(max_length=2, choices=[(b'ca', b'Category'), (b'ft', b'Full Text'), (b'da', b'Date'), (b'fl', b'Decimal Number')])),
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
            name='WorkflowDataMappingRevisionColumnLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('user_column_data_mapping', models.ForeignKey(to='workflow.UserColumnDataMapping')),
                ('workflow_data_column_revision', models.ForeignKey(to='workflow.WorkflowDataColumnsRevision')),
            ],
            options={
                'ordering': (b'-modified', b'-created'),
                'abstract': False,
                'get_latest_by': b'modified',
            },
            bases=(models.Model,),
        ),
    ]
