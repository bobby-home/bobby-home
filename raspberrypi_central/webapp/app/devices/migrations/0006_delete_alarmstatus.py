# Generated by Django 3.0.2 on 2020-02-03 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0005_alarmstatus'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AlarmStatus',
        ),
    ]