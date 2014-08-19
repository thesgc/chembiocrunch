# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='IC50Visualisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('x_axis', models.CharField(default=b'Destination Concentration', max_length=200)),
                ('y_axis', models.CharField(default=b'Percent inhibition', max_length=200)),
                ('compound_id', models.CharField(max_length=200)),
                ('error_bars', models.NullBooleanField()),
                ('results', models.TextField(default=b'{}')),
                ('visualisation_title', models.CharField(max_length=200, null=True, blank=True)),
                ('config_json', models.TextField(default=b'{}')),
                ('html', models.TextField(default=b'')),
                ('constrained', models.NullBooleanField()),
            ],
            options={
                'ordering': (b'-modified', b'-created'),
                'abstract': False,
                'get_latest_by': b'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IC50Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('title', models.CharField(max_length=100)),
                ('uploaded_config_file', models.FileField(max_length=1024, upload_to=b'')),
                ('uploaded_data_file', models.FileField(max_length=1024, upload_to=b'')),
                ('uploaded_meta_file', models.FileField(max_length=1024, upload_to=b'')),
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
            name='IC50WorkflowRevision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('steps_json', models.TextField(default=b'[]')),
                ('revision_type', models.CharField(max_length=5)),
                ('workflow', models.ForeignKey(to='ic50.IC50Workflow')),
            ],
            options={
                'ordering': (b'-modified', b'-created'),
                'abstract': False,
                'get_latest_by': b'modified',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ic50visualisation',
            name='data_mapping_revision',
            field=models.ForeignKey(to='ic50.IC50WorkflowRevision'),
            preserve_default=True,
        ),
    ]
