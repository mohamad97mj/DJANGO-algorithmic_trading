from django.db import models
from django.utils import timezone


class FuturesStoploss(models.Model):
    trigger_price = models.FloatField()
    is_triggered = models.BooleanField(default=False)
    is_trailed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
