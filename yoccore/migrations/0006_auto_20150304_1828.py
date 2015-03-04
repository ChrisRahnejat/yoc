# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yoccore', '0005_auto_20150302_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cleanedanswer',
            name='topic',
            field=models.CharField(blank=True, max_length=2, null=True, choices=[(b'GM', b'Gamification'), (b'FA', b'Financial analysis'), (b'LE', b'Life events'), (b'LF', b'Look and feel'), (b'BR', b'Branch setup'), (b'OT', b'Other')]),
            preserve_default=True,
        ),
    ]
