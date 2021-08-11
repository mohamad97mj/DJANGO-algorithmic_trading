from django.db import models


class SpotStep(models.Model):
    buy_price = models.FloatField()
    share = models.FloatField()
    is_triggered = models.BooleanField(default=False)
