# Generated by Django 3.2.7 on 2021-12-27 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0029_futuresposition_purchased_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='futuressignal',
            name='risk_level',
            field=models.CharField(default='medium', max_length=20),
        ),
    ]
