from django.db import models
from django.utils import timezone


class SpotPositionManager(models.Manager):
    pass


class SpotPosition(models.Model):
    objects = SpotPositionManager()

    # position_id = models.CharField(max_length=100, unique=True)
    signal = models.ForeignKey('SpotSignal', related_name='positions', on_delete=models.CASCADE, null=True, blank=True)
    amount_in_quote = models.FloatField()  # initial volume
    holding_amount = models.FloatField(default=0)
    released_amount_in_quote = models.FloatField(default=0)
    # current volume = ?
    keep_open = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
