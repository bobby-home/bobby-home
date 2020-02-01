# Generated by Django 3.0.2 on 2020-01-21 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0004_auto_20200117_1522'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=60)),
            ],
        ),
        migrations.AddField(
            model_name='alert',
            name='alert_type',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='devices.AlertType'),
            preserve_default=False,
        ),
    ]