from django.db import models
from django.utils import timezone


class FuturesTarget(models.Model):

    signal = models.ForeignKey('FuturesSignal', related_name='targets', on_delete=models.CASCADE)
    tp_price = models.FloatField()
    share = models.FloatField(default=0)
    holding_size = models.FloatField(default=0)
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
