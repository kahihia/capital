# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-25 17:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user_coins',
            old_name='total_investment_inr',
            new_name='total_investment',
        ),
        migrations.RemoveField(
            model_name='user_coins',
            name='total_investment_usd',
        ),
        migrations.RemoveField(
            model_name='user_coins',
            name='total_investment_value_inr',
        ),
        migrations.RemoveField(
            model_name='user_coins',
            name='total_investment_value_usd',
        ),
    ]
