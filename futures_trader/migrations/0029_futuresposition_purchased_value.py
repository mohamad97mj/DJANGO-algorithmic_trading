# Generated by Django 3.2.7 on 2021-12-25 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0028_remove_futuresstep_leverage'),
    ]

    operations = [
        migrations.AddField(
            model_name='futuresposition',
            name='purchased_value',
            field=models.FloatField(default=0),
        ),
    ]
