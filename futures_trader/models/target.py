from django.db import models
from django.utils import timezone


class FuturesTarget(models.Model):
    signal = models.ForeignKey('FuturesSignal', related_name='targets', on_delete=models.CASCADE)
    tp_price = models.FloatField()
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
