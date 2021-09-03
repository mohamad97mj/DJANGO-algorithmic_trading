from django.db import models
from django.utils import timezone


class FuturesOrder(models.Model):
    # order_id = models.CharField(max_length=100, unique=True)
    exchange_order_id = models.CharField(max_length=100, null=True, blank=True)
    datetime = models.DateTimeField(null=True, blank=True)
    timestamp = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    symbol = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    side = models.CharField(max_length=50)
    price = models.FloatField()
    average = models.FloatField(null=True, blank=True)
    size = models.FloatField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)
    leverage = models.IntegerField(null=True, blank=True)
    cost = models.FloatField(null=True, blank=True)
    filled_value = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
