# Generated by Django 3.2.7 on 2021-09-23 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spot_trader', '0010_alter_spottarget_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spotsignal',
            name='target_share_set_mode',
        ),
        migrations.AlterField(
            model_name='spottarget',
            name='share',
            field=models.FloatField(default=0),
        ),
    ]
