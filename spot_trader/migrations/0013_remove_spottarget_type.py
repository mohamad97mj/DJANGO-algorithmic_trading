# Generated by Django 3.2.7 on 2021-09-23 16:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spot_trader', '0012_alter_spottarget_share'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='spottarget',
            name='type',
        ),
    ]
