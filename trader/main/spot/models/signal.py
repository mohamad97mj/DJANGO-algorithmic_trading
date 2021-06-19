from datetime import datetime
from django.db import models
from django.contrib.postgres.fields import ArrayField


class SpotSignal(models.Model):
    signal_id = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=50)
    steps = ArrayField(models.FloatField())
    targets = ArrayField(models.FloatField())
    stop_loss = models.FloatField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = datetime.now()
        self.signal_id = '{}|{}'.format('signal', now)
