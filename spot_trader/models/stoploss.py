from django.db import models
from django.utils import timezone


class SpotStoploss(models.Model):
    trigger_price = models.FloatField()
    is_triggered = models.BooleanField(default=False)
    # is_trailed = models.BooleanField(default=False)

    operation = models.OneToOneField('SpotOperation', related_name='stoploss', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
