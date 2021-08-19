from django.db import models
from django.utils import timezone


class SpotTarget(models.Model):
    signal = models.ForeignKey('SpotSignal', related_name='targets', on_delete=models.CASCADE)
    tp_price = models.FloatField()
    share = models.FloatField(null=True, blank=True)
    is_triggered = models.BooleanField(default=False)
    amount = models.FloatField(default=0)
    cost = models.FloatField(default=0)
    operation = models.OneToOneField('SpotOperation', related_name='target', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
