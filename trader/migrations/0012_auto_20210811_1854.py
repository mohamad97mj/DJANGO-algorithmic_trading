# Generated by Django 3.2.3 on 2021-08-11 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trader', '0011_auto_20210811_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotstep',
            name='share',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='spottarget',
            name='share',
            field=models.FloatField(null=True),
        ),
    ]
