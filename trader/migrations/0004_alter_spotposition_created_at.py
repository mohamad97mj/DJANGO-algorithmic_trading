# Generated by Django 3.2.3 on 2021-06-30 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trader', '0003_auto_20210630_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotposition',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
