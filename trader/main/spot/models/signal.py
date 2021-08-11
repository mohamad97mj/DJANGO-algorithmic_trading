from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import ArrayField


class SpotSignal(models.Model):
    # signal_id = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=50)
    stoploss = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
