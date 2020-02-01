# Generated by Django 3.0.2 on 2020-02-01 14:35

import devices.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='severity',
            field=models.CharField(choices=[(devices.models.SeverityChoice['LOW'], 'low'), (devices.models.SeverityChoice['MODERATE'], 'moderate'), (devices.models.SeverityChoice['HIGH'], 'high')], max_length=60),
        ),
    ]
