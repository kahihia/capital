# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-01-29 12:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_auto_20180126_0042'),
    ]

    operations = [
        migrations.AddField(
            model_name='trading_platform',
            name='client_id',
            field=models.CharField(default='23232', max_length=100)

        ),
    ]