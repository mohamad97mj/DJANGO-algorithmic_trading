# Generated by Django 3.2.3 on 2021-08-19 14:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trader', '0018_spotoperation_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotoperation',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operations', to='trader.spotposition'),
        ),
    ]