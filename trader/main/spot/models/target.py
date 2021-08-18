from django.db import models
from django.utils import timezone


class SpotTarget(models.Model):
    signal = models.ForeignKey('SpotSignal', related_name='targets', on_delete=models.CASCADE)
    tp_price = models.FloatField()
    share = models.FloatField(null=True, blank=True)
    is_triggered = models.BooleanField(default=False)
    amount = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
