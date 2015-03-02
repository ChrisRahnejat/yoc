# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yoccore', '0002_remove_cleanedanswer_intepretation'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='done',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
