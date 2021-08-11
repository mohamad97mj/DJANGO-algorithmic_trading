from django.db import models
from django.utils import timezone


class SpotTarget(models.Model):
    signal = models.ForeignKey('SpotSignal', related_name='targets', on_delete=models.CASCADE, null=True)
    tp_price = models.FloatField()
    share = models.FloatField()
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
