# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-05-17 02:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynaform', '0002_auto_20160510_0504'),
    ]

    operations = [
        migrations.AddField(
            model_name='legaltemplates',
            name='group',
            field=models.CharField(default='form_group', max_length=255),
        ),
        migrations.AddField(
            model_name='legaltemplates',
            name='slug',
            field=models.SlugField(default='abc'),
        ),
    ]
