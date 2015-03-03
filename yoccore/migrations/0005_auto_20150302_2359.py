# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yoccore', '0004_auto_20150302_1736'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cleanedanswer',
            options={'verbose_name': 'cleaned answer'},
        ),
        migrations.AlterField(
            model_name='cleanedanswer',
            name='quotable',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='cleanedanswer',
            name='rating',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='cleanedanswer',
            name='topic',
            field=models.CharField(blank=True, max_length=2, null=True, choices=[(b'GM', b'Gamification'), (b'FA', b'Financial analysis'), (b'LE', b'Life events'), (b'LF', b'Look and feel'), (b'OT', b'Other')]),
            preserve_default=True,
        ),
    ]
