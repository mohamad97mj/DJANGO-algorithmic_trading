# Generated by Django 3.2.3 on 2021-09-03 12:43

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FuturesOperation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100)),
                ('action', models.CharField(max_length=50)),
                ('status', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='FuturesOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('datetime', models.DateTimeField(blank=True, null=True)),
                ('timestamp', models.BigIntegerField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=50, null=True)),
                ('symbol', models.CharField(max_length=50)),
                ('type', models.CharField(max_length=50)),
                ('side', models.CharField(max_length=50)),
                ('price', models.FloatField()),
                ('average', models.FloatField(blank=True, null=True)),
                ('size', models.FloatField(blank=True, null=True)),
                ('value', models.FloatField(blank=True, null=True)),
                ('leverage', models.IntegerField(blank=True, null=True)),
                ('cost', models.FloatField(blank=True, null=True)),
                ('filled_value', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='FuturesSignal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('step_share_set_mode', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='FuturesTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tp_price', models.FloatField()),
                ('is_triggered', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('signal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='targets', to='futures_trader.futuressignal')),
            ],
        ),
        migrations.CreateModel(
            name='FuturesStoploss',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trigger_price', models.FloatField()),
                ('is_triggered', models.BooleanField(default=False)),
                ('is_trailed', models.BooleanField(default=False)),
                ('size', models.FloatField(default=0)),
                ('released_margin', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('operation', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stoploss', to='futures_trader.futuresoperation')),
            ],
        ),
        migrations.CreateModel(
            name='FuturesStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buy_price', models.FloatField()),
                ('share', models.FloatField(blank=True, null=True)),
                ('is_triggered', models.BooleanField(default=False)),
                ('size', models.FloatField(blank=True, null=True)),
                ('cost', models.FloatField(default=0)),
                ('purchased_value', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('operation', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='step', to='futures_trader.futuresoperation')),
                ('signal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='futures_trader.futuressignal')),
            ],
        ),
        migrations.AddField(
            model_name='futuressignal',
            name='stoploss',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='signal', to='futures_trader.futuresstoploss'),
        ),
        migrations.CreateModel(
            name='FuturesPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.FloatField(blank=True, null=True)),
                ('margin', models.FloatField(blank=True, null=True)),
                ('leverage', models.IntegerField()),
                ('keep_open', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('signal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='futures_trader.futuressignal')),
            ],
        ),
        migrations.AddField(
            model_name='futuresoperation',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, related_name='operation', to='futures_trader.futuresorder'),
        ),
        migrations.AddField(
            model_name='futuresoperation',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operations', to='futures_trader.futuresposition'),
        ),
        migrations.CreateModel(
            name='FuturesBot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange_id', models.CharField(max_length=100)),
                ('credential_id', models.CharField(max_length=100)),
                ('strategy', models.CharField(max_length=100)),
                ('total_pnl', models.FloatField(default=0)),
                ('total_pnl_percentage', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('status', models.CharField(default='running', max_length=50)),
                ('position', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bot', to='futures_trader.futuresposition')),
            ],
        ),
    ]
