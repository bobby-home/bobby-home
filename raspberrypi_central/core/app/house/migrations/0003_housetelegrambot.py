# Generated by Django 3.0.7 on 2020-08-02 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('house', '0002_house'),
    ]

    operations = [
        migrations.CreateModel(
            name='HouseTelegramBot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=80)),
            ],
        ),
    ]