# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2019-04-11 10:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('classes', '0002_auto_20190410_1630'),
        ('attendance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='classes',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='classes.Classes', verbose_name='\u73ed\u7ea7'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='date',
            field=models.DateField(auto_now_add=True, null=True, verbose_name='\u8003\u52e4\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='submitter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='\u586b\u62a5\u4eba'),
        ),
        migrations.AlterField(
            model_name='absence',
            name='submit_notes',
            field=models.CharField(blank=True, help_text='\u586b\u5199\u6536\u6b3e\u4eba\u7684\u94f6\u884c\u5361\u4fe1\u606f\uff0c\u5361\u53f7\u3001\u6301\u5361\u4eba\u3001\u5f00\u6237\u884c', max_length=200, null=True, verbose_name='\u63d0\u4ea4\u5907\u6ce8'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='\u586b\u62a5\u65f6\u95f4'),
        ),
    ]
