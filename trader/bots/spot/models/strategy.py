from django.db import models


class SpotStrategy(models.Model):
    id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
