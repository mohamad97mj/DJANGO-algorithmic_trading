from django.db import models


class SpotTarget(models.Model):
    tp_price = models.FloatField()
    share = models.FloatField()
    is_triggered = models.BooleanField(default=False)
