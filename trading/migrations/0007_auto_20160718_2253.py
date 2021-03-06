# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-18 17:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0006_auto_20160630_0053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calls',
            name='entry_price',
        ),
        migrations.AddField(
            model_name='calls',
            name='entry_price_range',
            field=models.CharField(default=-900, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='calls',
            name='trade',
            field=models.CharField(choices=[('BUY', 'BUY'), ('SELL', 'SELL')], default='BUY', max_length=3),
        ),
        migrations.AlterField(
            model_name='calls',
            name='time_frame',
            field=models.CharField(blank=True, default='1 Day', max_length=100),
        ),
    ]
