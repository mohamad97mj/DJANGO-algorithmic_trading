# Generated by Django 3.2.3 on 2021-09-07 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0004_remove_futuresstep_purchased_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='futuresposition',
            name='size',
            field=models.FloatField(default=0),
        ),
    ]
