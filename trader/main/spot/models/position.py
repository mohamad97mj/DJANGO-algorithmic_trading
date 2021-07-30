from django.db import models
from django.utils import timezone


class SpotPositionManager(models.Manager):
    pass


class SpotPosition(models.Model):
    objects = SpotPositionManager()

    # position_id = models.CharField(max_length=100, unique=True)
    signal = models.ForeignKey('SpotSignal', related_name='positions', on_delete=models.RESTRICT, null=True)
    volume = models.FloatField()  # initial volume
    # current volume = ?
    created_at = models.CharField(max_length=100, default=timezone.now, blank=True)
