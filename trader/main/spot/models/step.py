from django.db import models
from django.utils import timezone


class SpotStep(models.Model):
    signal = models.ForeignKey('SpotSignal', related_name='steps', on_delete=models.CASCADE)
    buy_price = models.FloatField()
    share = models.FloatField(null=True, blank=True)
    is_triggered = models.BooleanField(default=False)
    amount_in_quote = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
