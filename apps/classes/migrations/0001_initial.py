# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2019-04-10 11:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import libs.filefield


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Classes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='\u73ed\u7ea7\u540d')),
                ('introduction', models.CharField(max_length=200, verbose_name='\u73ed\u7ea7\u4ecb\u7ecd')),
            ],
            options={
                'default_permissions': (),
                'db_table': 'classes',
                'verbose_name': '\u73ed\u7ea7\u7ba1\u7406',
            },
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='\u5e74\u7ea7\u540d')),
                ('introduction', models.CharField(max_length=200, verbose_name='\u5e74\u7ea7\u4ecb\u7ecd')),
            ],
            options={
                'default_permissions': (),
                'db_table': 'grade',
                'verbose_name': '\u5e74\u7ea7\u7ba1\u7406',
            },
        ),
        migrations.CreateModel(
            name='Kindergarten',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='\u5e7c\u513f\u56ed\u540d\u5b57')),
                ('address', models.CharField(blank=True, max_length=200, null=True, verbose_name='\u5e7c\u513f\u56ed\u5730\u5740')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='\u5907\u6ce8\u4fe1\u606f')),
                ('account_book', models.CharField(max_length=50, verbose_name='\u8d26\u5957')),
            ],
            options={
                'default_permissions': (),
                'db_table': 'kindergarten',
                'verbose_name': '\u5e7c\u513f\u56ed\u7ba1\u7406',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=10, null=True, verbose_name='\u540d\u5b57')),
                ('icon', models.ImageField(blank=True, null=True, upload_to=libs.filefield.PathAndRename(b'user/student'), verbose_name='\u5934\u50cf')),
                ('age', models.IntegerField(blank=True, null=True, verbose_name='\u5e74\u9f84')),
                ('gender', models.PositiveSmallIntegerField(choices=[(1, '\u5973'), (2, '\u7537')], default=1, verbose_name='\u6027\u522b')),
                ('notes', models.CharField(blank=True, max_length=200, null=True, verbose_name='\u5907\u6ce8\u4fe1\u606f')),
                ('classes', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='classes_students', to='classes.Classes', verbose_name='\u73ed\u7ea7')),
            ],
            options={
                'default_permissions': (),
                'db_table': 'student',
                'verbose_name': '\u5b66\u751f',
            },
        ),
        migrations.AddField(
            model_name='grade',
            name='kindergarten',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='kinder_grades', to='classes.Kindergarten', verbose_name='\u5e7c\u513f\u56ed'),
        ),
        migrations.AddField(
            model_name='classes',
            name='grade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='grade_classes', to='classes.Grade', verbose_name='\u5e74\u7ea7'),
        ),
    ]