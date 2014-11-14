# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0015_merge'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='IcFiftyWorkflow',
            new_name='IC50Workflow',
        ),
        migrations.CreateModel(
            name='IC50WorkflowRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('steps_json', models.TextField(default=b'[]')),
                ('revision_type', models.CharField(max_length=5)),
                ('workflow', models.ForeignKey(to='workflow.IC50Workflow')),
            ],
            options={
                'ordering': (b'-modified', b'-created'),
                'abstract': False,
                'get_latest_by': b'modified',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='icfiftyworkflowdatamappingrevision',
            name='workflow',
        ),
        migrations.DeleteModel(
            name='IcFiftyWorkflowDataMappingRevision',
        ),
        migrations.AlterField(
            model_name='visualisation',
            name='config_json',
            field=models.TextField(default=b'{}'),
        ),
    ]
