# Generated by Django 3.2.3 on 2021-08-10 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trader', '0007_alter_spotsignal_step_weights'),
    ]

    operations = [
        migrations.RenameField(
            model_name='spotsignal',
            old_name='step_weights',
            new_name='step_shares',
        ),
        migrations.RenameField(
            model_name='spotsignal',
            old_name='target_weights',
            new_name='target_shares',
        ),
    ]