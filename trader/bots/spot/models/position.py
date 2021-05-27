from django.db import models


class SpotPosition(models.Model):
    position_id = models.CharField(max_length=100, unique=True)
    signal = models.ForeignKey('SpotSignal', related_name='positions', on_delete=models.RESTRICT)
    volume = models.FloatField()
    strategy = models.OneToOneField('SpotStrategy', related_name='position', on_delete=models.RESTRICT)
