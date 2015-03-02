# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yoccore', '0003_answer_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='cleanedanswer',
            name='not_feedback',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(max_length=2, choices=[(b'TX', b'text'), (b'NM', b'numerical'), (b'PD', b'personal details'), (b'EN', b'from enums'), (b'SG', b'name suggestions')]),
            preserve_default=True,
        ),
    ]
