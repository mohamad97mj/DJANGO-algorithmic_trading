from django.db import models
from django.contrib.postgres.fields import ArrayField


class Signal(models.Model):
    symbol = models.CharField(max_length=50)
    steps = ArrayField(models.FloatField())
    targets = ArrayField(models.FloatField())
    stop_loss = models.FloatField()
