from django.db import models
from django.utils import timezone


class SpotPositionManager(models.Manager):
    pass


class SpotPosition(models.Model):
    objects = SpotPositionManager()

    # position_id = models.CharField(max_length=100, unique=True)
    signal = models.ForeignKey('SpotSignal', related_name='positions', on_delete=models.CASCADE, null=True, blank=True)
    size = models.FloatField()  # initial volume
    # current volume = ?
    keep_open = models.BooleanField()
    created_at = models.DateTimeField(default=timezone.now, blank=True)
