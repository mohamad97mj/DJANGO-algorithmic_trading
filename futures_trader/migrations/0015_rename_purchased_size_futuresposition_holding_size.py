# Generated by Django 3.2.7 on 2021-09-14 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0014_auto_20210912_2258'),
    ]

    operations = [
        migrations.RenameField(
            model_name='futuresposition',
            old_name='purchased_size',
            new_name='holding_size',
        ),
    ]
