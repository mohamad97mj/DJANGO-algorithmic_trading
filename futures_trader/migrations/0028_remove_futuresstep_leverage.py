# Generated by Django 3.2.7 on 2021-12-24 15:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0027_auto_20211223_1233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='futuresstep',
            name='leverage',
        ),
    ]
