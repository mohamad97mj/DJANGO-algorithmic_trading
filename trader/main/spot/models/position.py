from django.db import models
from datetime import datetime
from .utils import TimeFieldTZ


class SpotPositionManager(models.Manager):
    pass


class SpotPosition(models.Model):
    objects = SpotPositionManager()

    # position_id = models.CharField(max_length=100, unique=True)
    signal = models.ForeignKey('SpotSignal', related_name='positions', on_delete=models.RESTRICT, null=True)
    volume = models.FloatField()
    created_at = TimeFieldTZ(default=datetime.now, blank=True)
