# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-01-29 13:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0020_auto_20180129_1846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trading_platform',
            name='client_id',
            field=models.IntegerField(max_length=100),
        ),
    ]
