# Generated by Django 3.2.3 on 2021-08-19 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trader', '0015_auto_20210819_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='spotoperation',
            name='type',
            field=models.CharField(max_length=100, null=True),
        ),
    ]