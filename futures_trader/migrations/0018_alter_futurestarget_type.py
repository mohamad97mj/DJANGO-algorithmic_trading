# Generated by Django 3.2.7 on 2021-09-23 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('futures_trader', '0017_alter_futurestarget_share'),
    ]

    operations = [
        migrations.AlterField(
            model_name='futurestarget',
            name='type',
            field=models.CharField(choices=[('tp', 'Tp'), ('trail_and_tp', 'Trail And Tp')], max_length=20),
        ),
    ]
