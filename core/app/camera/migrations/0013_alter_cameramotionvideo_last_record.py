# Generated by Django 3.2 on 2022-01-28 23:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('camera', '0012_cameramotionvideo_last_record'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cameramotionvideo',
            name='last_record',
            field=models.DateTimeField(),
        ),
    ]