# Generated by Django 3.2.7 on 2021-11-12 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0024_auto_20211112_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='futuresposition',
            name='leverage',
            field=models.IntegerField(default=0),
        ),
    ]