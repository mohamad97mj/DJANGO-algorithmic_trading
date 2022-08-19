from django.db import models
from django.utils import timezone


class FuturesPositionManager(models.Manager):
    pass


class FuturesPosition(models.Model):
    objects = FuturesPositionManager()

    # position_id = models.CharField(max_length=100, unique=True)
    signal = models.ForeignKey('FuturesSignal',
                               related_name='positions',
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True)
    holding_size = models.FloatField(default=0)
    margin = models.FloatField()
    keep_open = models.BooleanField(default=False)
    purchased_value = models.FloatField(default=0)
    released_margin = models.FloatField(default=0)
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
