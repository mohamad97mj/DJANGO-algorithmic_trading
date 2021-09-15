from django.db import models
from django.utils import timezone


class FuturesPositionManager(models.Manager):
    pass


class FuturesPosition(models.Model):
    objects = FuturesPositionManager()

    # position_id = models.CharField(max_length=100, unique=True)
    signal = models.ForeignKey('FuturesSignal', related_name='positions', on_delete=models.CASCADE, null=True, blank=True)
    holding_size = models.FloatField(default=0)
    margin = models.FloatField()
    leverage = models.IntegerField()
    keep_open = models.BooleanField(default=False)
    released_margin = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
