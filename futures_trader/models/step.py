from django.db import models


class FuturesStep(models.Model):
    signal = models.ForeignKey('FuturesSignal', related_name='steps', on_delete=models.CASCADE)
    entry_price = models.FloatField()
    share = models.FloatField(null=True, blank=True)
    margin = models.FloatField(null=True, blank=True)
    is_market = models.BooleanField(default=False)
    is_triggered = models.BooleanField(default=False)
    purchased_size = models.FloatField(null=True, blank=True)
    cost = models.FloatField(default=0)
    operation = models.OneToOneField('FuturesOperation', related_name='step', on_delete=models.SET_NULL, null=True)
