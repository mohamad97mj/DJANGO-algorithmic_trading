from django.db import models


class SpotPosition:
    signal = models.ForeignKey('SpotSignal', on_delete=models.RESTRICT)
    volume = models.FloatField()
    strategy = models.ForeignKey('SpotStrategy', on_delete=models.RESTRICT)
