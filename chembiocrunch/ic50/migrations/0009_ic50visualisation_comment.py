# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0008_auto_20141016_0921'),
    ]

    operations = [
        migrations.AddField(
            model_name='ic50visualisation',
            name='comment',
            field=models.CharField(default=b'Good Curve', max_length=30, choices=[(b'Good Curve', b'Good Curve'), (b'Top plateaus at below 80%', b'Top plateaus at below 80%'), (b'Bottom plateaus above 20%', b'Bottom plateaus above 20%'), (b'Top plateaus above 120 %', b'Top plateaus above 120 %'), (b'Bottom plateaus below- 20%', b'Bottom plateaus below- 20%'), (b'incomplete curve', b'incomplete curve'), (b'poor curve', b'poor curve'), (b'inactive compound', b'inactive compound'), (b'steep hillslope', b'steep hillslope'), (b'Top of curve does not plateaux', b'Top of curve does not plateaux')]),
            preserve_default=True,
        ),
    ]
