# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0019_auto_20140813_1606'),
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
                ('visualisation_title', models.CharField(max_length=200, null=True, blank=True)),
                ('config_json', models.TextField(default=b'{}')),
                ('html', models.TextField(default=b'')),
                ('data_mapping_revision', models.ForeignKey(to='workflow.IC50WorkflowRevision')),
            ],
            options={
                'ordering': (b'-modified', b'-created'),
                'abstract': False,
                'get_latest_by': b'modified',
            },
            bases=(models.Model,),
        ),
    ]
