# Generated by Django 3.0.3 on 2020-05-15 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('alarm', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alarmstatus',
            old_name='is_active',
            new_name='running',
        ),
    ]