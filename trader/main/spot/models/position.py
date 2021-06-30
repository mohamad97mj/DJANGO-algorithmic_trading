from django.db import models
from datetime import datetime


class SpotPositionManager(models.Manager):
    pass


class SpotPosition(models.Model):
    objects = SpotPositionManager()

    position_id = models.CharField(max_length=100, unique=True)
    signal = models.ForeignKey('SpotSignal', related_name='positions', on_delete=models.RESTRICT)
    volume = models.FloatField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = datetime.now()
        self.position_id = '{}|{}'.format('position', now)
