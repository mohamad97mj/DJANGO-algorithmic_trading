from django.db import models


class FuturesStep(models.Model):
    signal = models.ForeignKey('FuturesSignal', related_name='steps', on_delete=models.CASCADE)
    entry_price = models.FloatField()
    share = models.FloatField(null=True, blank=True)
    leverage = models.IntegerField(null=True, blank=True)
    is_triggered = models.BooleanField(default=False)
    margin = models.FloatField(null=True, blank=True)
    purchased_size = models.FloatField(null=True, blank=True)
    is_market = models.BooleanField(default=False)
    cost = models.FloatField(default=0)
    operation = models.OneToOneField('FuturesOperation', related_name='step', on_delete=models.SET_NULL, null=True)
