from django.db import models


class SpotOrder(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    datetime = models.DateTimeField()
    timestamp = models.BigIntegerField()
    status = models.CharField(max_length=50)
    symbol = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    side = models.CharField(max_length=50)
    price = models.FloatField()
    average = models.FloatField()
    amount = models.FloatField()
    filled = models.FloatField()
    remaining = models.FloatField()
    cost = models.FloatField()
    fee = models.JSONField()
