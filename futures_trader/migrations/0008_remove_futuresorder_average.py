# Generated by Django 3.2.3 on 2021-09-07 17:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0007_auto_20210907_1852'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='futuresorder',
            name='average',
        ),
    ]
