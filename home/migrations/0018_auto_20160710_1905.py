# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-10 13:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0017_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='contact',
            field=models.CharField(max_length=13),
        ),
        migrations.AlterField(
            model_name='contact',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
