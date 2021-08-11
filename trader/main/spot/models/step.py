from django.db import models
from django.utils import timezone


class SpotStep(models.Model):
    signal = models.ForeignKey('SpotSignal', related_name='steps', on_delete=models.CASCADE, null=True)
    buy_price = models.FloatField()
    share = models.FloatField()
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
