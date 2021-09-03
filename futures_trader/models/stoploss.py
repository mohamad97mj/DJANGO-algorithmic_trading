from django.db import models
from django.utils import timezone


class FuturesStoploss(models.Model):
    trigger_price = models.FloatField()
    is_triggered = models.BooleanField(default=False)
    is_trailed = models.BooleanField(default=False)
    size = models.FloatField(default=0)
    released_value = models.FloatField(default=0)
    operation = models.OneToOneField('FuturesOperation', related_name='stoploss', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)