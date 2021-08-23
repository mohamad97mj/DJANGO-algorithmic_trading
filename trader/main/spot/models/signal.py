from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import ArrayField


class SpotSignal(models.Model):
    # signal_id = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=50)
    stoploss = models.OneToOneField('SpotStoploss', related_name='signal', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    step_share_set_mode = models.CharField(default="manual", max_length=50)
    target_share_set_mode = models.CharField(default="manual", max_length=50)
