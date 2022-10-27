# Generated by Django 3.2.12 on 2022-10-27 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0041_auto_20221020_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='futuresflatresistancetradezone',
            name='is_major',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='futuresflatsupporttradezone',
            name='is_major',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='futuresinclineresistancetradezone',
            name='is_major',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='futuresinclinesupporttradezone',
            name='is_major',
            field=models.BooleanField(default=False),
        ),
    ]
