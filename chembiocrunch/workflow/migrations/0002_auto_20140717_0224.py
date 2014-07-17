# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkflowDataColumnsRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('steps_json', models.TextField(default=b'[]')),
            ],
            options={
                'ordering': (b'-modified', b'-created'),
                'abstract': False,
                'get_latest_by': b'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WorkflowDataMappingRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('steps_json', models.TextField(default=b'[]')),
                ('workflow', models.ForeignKey(to='workflow.Workflow')),
            ],
            options={
                'ordering': (b'-modified', b'-created'),
                'abstract': False,
                'get_latest_by': b'modified',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='workflowdatacolumnsrevision',
            name='schema_revision',
            field=models.ForeignKey(to='workflow.WorkflowDataMappingRevision'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='workflowdatarevision',
            name='schema_revision',
        ),
        migrations.DeleteModel(
            name='WorkflowDataRevision',
        ),
        migrations.RemoveField(
            model_name='workflowschemarevision',
            name='workflow',
        ),
        migrations.DeleteModel(
            name='WorkflowSchemaRevision',
        ),
    ]
