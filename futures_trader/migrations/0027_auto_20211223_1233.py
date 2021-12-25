# Generated by Django 3.2.7 on 2021-12-23 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0026_alter_futuresposition_leverage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='futuresposition',
            name='leverage',
        ),
        migrations.AddField(
            model_name='futuressignal',
            name='leverage',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
