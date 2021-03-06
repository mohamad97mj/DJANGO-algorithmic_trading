# Generated by Django 3.2.7 on 2021-09-14 20:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spot_trader', '0005_auto_20210912_2258'),
    ]

    operations = [
        migrations.RenameField(
            model_name='spotposition',
            old_name='purchased_amount',
            new_name='holding_amount',
        ),
        migrations.RenameField(
            model_name='spottarget',
            old_name='purchased_amount',
            new_name='holding_amount',
        ),
        migrations.RemoveField(
            model_name='spotorder',
            name='average',
        ),
        migrations.RemoveField(
            model_name='spotorder',
            name='datetime',
        ),
        migrations.RemoveField(
            model_name='spotorder',
            name='pure_amount',
        ),
    ]
