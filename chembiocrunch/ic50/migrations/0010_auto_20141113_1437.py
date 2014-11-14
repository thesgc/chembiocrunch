# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ic50', '0009_ic50visualisation_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ic50visualisation',
            name='comment',
            field=models.CharField(default=b'Good Curve', max_length=30, choices=[(b'Good Curve', b'Good Curve'), (b'Top plateaus at below 80%', b'Top Plateaus at Below 80%'), (b'Bottom plateaus above 20%', b'Bottom Plateaus Above 20%'), (b'Top plateaus above 120 %', b'Top Plateaus Above 120 %'), (b'Bottom plateaus below- 20%', b'Bottom Plateaus Below- 20%'), (b'incomplete curve', b'Incomplete Curve'), (b'poor curve', b'Poor Curve'), (b'inactive compound', b'Inactive Compound'), (b'steep hillslope', b'Steep Hillslope'), (b'Top of curve does not plateaux', b'Top of Curve Does Not Plateaux')]),
        ),
    ]
