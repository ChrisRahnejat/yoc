# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('answer_text', models.TextField()),
            ],
            options={
                'verbose_name': 'answer',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CleanedAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('rating', models.IntegerField()),
                ('topic', models.CharField(max_length=2, choices=[(b'GM', b'Gamification'), (b'FA', b'Financial analysis'), (b'LE', b'Life events'), (b'LF', b'Look and feel'), (b'OT', b'Other')])),
                ('intepretation', models.TextField()),
                ('quotable', models.BooleanField()),
                ('answer', models.ForeignKey(to='yoccore.Answer')),
                ('real_type', models.ForeignKey(editable=False, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'session',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('question_text', models.TextField()),
                ('question_type', models.CharField(max_length=2, choices=[(b'TX', b'text'), (b'NM', b'numerical'), (b'PD', b'personal details'), (b'EN', b'from enums')])),
                ('question_page', models.IntegerField()),
                ('question_number', models.IntegerField()),
                ('real_type', models.ForeignKey(editable=False, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'question',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('session_key', models.CharField(max_length=50)),
                ('user_initials', models.CharField(max_length=5)),
                ('location', models.CharField(max_length=1, choices=[(b'M', b'Moorgate'), (b'S', b'Shoreditch')])),
                ('submit_date', models.DateField()),
                ('real_type', models.ForeignKey(editable=False, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'session',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(to='yoccore.Question'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='answer',
            name='real_type',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='answer',
            name='session',
            field=models.ForeignKey(to='yoccore.Session'),
            preserve_default=True,
        ),
    ]
