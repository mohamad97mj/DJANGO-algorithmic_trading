from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import ArrayField


class SpotSignal(models.Model):
    # signal_id = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=50)
    steps = ArrayField(models.FloatField())
    targets = ArrayField(models.FloatField())
    stoploss = models.FloatField()
    created_at = models.CharField(max_length=100, default=timezone.now, blank=True)
