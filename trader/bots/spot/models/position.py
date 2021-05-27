from django.db import models


class SpotPosition(models.Model):
    signal = models.ForeignKey('SpotSignal', related_name='positions', on_delete=models.RESTRICT)
    volume = models.FloatField()
    strategy = models.OneToOneField('SpotStrategy', related_name='position', on_delete=models.RESTRICT)
