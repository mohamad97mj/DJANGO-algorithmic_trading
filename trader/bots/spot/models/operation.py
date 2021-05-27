from django.db import models


class Operation(models.Model):
    order = models.ForeignKey('SpotOrder', on_delete=models.RESTRICT)
    action = models.CharField(max_length=50)
    is_done = models.BooleanField()
