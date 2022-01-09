# Generated by Django 3.2.7 on 2021-11-12 10:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0023_auto_20210924_1917'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='futuresstoploss',
            name='operation',
        ),
        migrations.AddField(
            model_name='futurestarget',
            name='operation',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='target', to='futures_trader.futuresoperation'),
        ),
        migrations.AlterField(
            model_name='futuresposition',
            name='leverage',
            field=models.IntegerField(null=True),
        ),
    ]