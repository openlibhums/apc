# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-11-09 10:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apc', '0014_merge_20200929_0856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingstaffer',
            name='type_of_notification',
            field=models.CharField(choices=[('ready', 'Ready for Invoicing'), ('invoiced', 'Invoice Sent'), ('paid', 'Invoice Paid'), ('waiver', 'Waiver Application')], default='ready', max_length=15),
        ),
    ]
