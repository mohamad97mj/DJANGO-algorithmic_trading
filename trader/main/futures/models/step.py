from django.db import models
from django.utils import timezone


class FuturesStep(models.Model):
    signal = models.ForeignKey('FuturesSignal', related_name='steps', on_delete=models.CASCADE)
    buy_price = models.FloatField()
    share = models.FloatField(null=True, blank=True)
    is_triggered = models.BooleanField(default=False)
    amount_in_quote = models.FloatField(null=True, blank=True)
    purchased_amount = models.FloatField(default=0)
    operation = models.OneToOneField('FuturesOperation', related_name='step', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)