# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-10 14:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_client', '0006_auto_20161009_2204'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitecode',
            name='createdby',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_by_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='invitecode',
            name='usedby',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='used_by_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
