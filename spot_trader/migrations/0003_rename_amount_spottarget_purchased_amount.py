# Generated by Django 3.2.7 on 2021-09-12 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spot_trader', '0002_auto_20210912_1926'),
    ]

    operations = [
        migrations.RenameField(
            model_name='spottarget',
            old_name='amount',
            new_name='purchased_amount',
        ),
    ]
