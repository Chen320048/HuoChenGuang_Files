# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2019-04-10 11:46
from __future__ import unicode_literals

import DjangoUeditor.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True, verbose_name='\u6d3b\u52a8\u6807\u9898')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, '\u8fdb\u884c\u4e2d'), (1, '\u5df2\u7ed3\u675f')], default=0, verbose_name='\u6d3b\u52a8\u72b6\u6001')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u53d1\u5e03\u65f6\u95f4')),
                ('close_time', models.DateTimeField(blank=True, null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4')),
                ('detail', DjangoUeditor.models.UEditorField(default=b'', verbose_name='\u6d3b\u52a8\u8be6\u60c5')),
                ('introduction', models.TextField(blank=True, null=True, verbose_name='\u6d3b\u52a8\u4ecb\u7ecd')),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='\u6d3b\u52a8\u53d1\u8d77\u4eba')),
            ],
            options={
                'default_permissions': (),
                'db_table': 'activity',
                'verbose_name': '\u6d3b\u52a8\u7ba1\u7406',
            },
        ),
    ]
