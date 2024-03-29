# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2019-04-11 09:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_auto_20190404_2012'),
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appid', models.IntegerField(verbose_name=b'AppID')),
                ('appsecret', models.CharField(max_length=255, verbose_name=b'App\xe7\xa7\x98\xe9\x92\xa5')),
                ('token', models.CharField(editable=False, max_length=255, verbose_name=b'\xe5\x85\xa8\xe5\xb1\x80token')),
                ('valid_term', models.PositiveIntegerField(editable=False, verbose_name=b'\xe6\x9c\x89\xe6\x95\x88\xe6\x97\xb6\xe9\x95\xbf')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe4\xb8\x8a\xe6\xac\xa1\xe6\x9b\xb4\xe6\x94\xb9\xe6\x97\xb6\xe9\x97\xb4')),
            ],
        ),
    ]
