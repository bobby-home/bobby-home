# Generated by Django 3.2 on 2021-08-12 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0006_alter_device_mac_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicetype',
            name='type',
            field=models.CharField(default=None, max_length=100, primary_key=True, serialize=False),
        ),
    ]