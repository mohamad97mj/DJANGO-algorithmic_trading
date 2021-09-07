# Generated by Django 3.2.3 on 2021-09-03 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='futuresstep',
            name='margin',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='futuresposition',
            name='margin',
            field=models.FloatField(),
        ),
    ]
