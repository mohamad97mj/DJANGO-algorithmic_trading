from django.db import models


class SpotStrategy(models.Model):
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    bot = models.ForeignKey('SpotBot', related_name='strategies', on_delete=models.RESTRICT)
