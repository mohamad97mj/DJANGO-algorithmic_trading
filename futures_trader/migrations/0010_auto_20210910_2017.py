# Generated by Django 3.2.7 on 2021-09-10 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0009_auto_20210908_1302'),
    ]

    operations = [
        migrations.RenameField(
            model_name='futuresstep',
            old_name='buy_price',
            new_name='entry_price',
        ),
        migrations.AddField(
            model_name='futuressignal',
            name='side',
            field=models.CharField(default='long', max_length=10),
            preserve_default=False,
        ),
    ]
