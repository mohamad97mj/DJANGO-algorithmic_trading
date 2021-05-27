from django.db import models


class SpotPosition(models.Model):
    signal = models.ForeignKey('SpotSignal', on_delete=models.RESTRICT)
    volume = models.FloatField()
    strategy = models.ForeignKey('SpotStrategy', related_name='position', on_delete=models.RESTRICT)
