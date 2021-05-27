from django.db import models


class SpotOrder(models.Model):
    order_id = models.CharField(max_length=100, unique=True, blank=True)
    datetime = models.DateTimeField(blank=True)
    timestamp = models.BigIntegerField(blank=True)
    status = models.CharField(max_length=50, blank=True)
    symbol = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    side = models.CharField(max_length=50)
    price = models.FloatField()
    average = models.FloatField(blank=True)
    amount = models.FloatField()
    filled = models.FloatField()
    remaining = models.FloatField()
    cost = models.FloatField()
    fee = models.JSONField()
