# Generated by Django 3.2.3 on 2021-08-19 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trader', '0016_spotoperation_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotoperation',
            name='type',
            field=models.CharField(max_length=100),
        ),
    ]