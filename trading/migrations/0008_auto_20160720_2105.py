# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-20 15:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0007_auto_20160718_2253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calls',
            name='trade',
            field=models.CharField(choices=[('BUY', 'BUY'), ('SELL', 'SELL')], default='BUY', max_length=4),
        ),
    ]
