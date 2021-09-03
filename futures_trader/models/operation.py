from django.db import models
from django.utils import timezone


class FuturesOperation(models.Model):
    # operation_id = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=100)
    position = models.ForeignKey('FuturesPosition', related_name='operations', on_delete=models.CASCADE)
    order = models.OneToOneField('FuturesOrder', related_name='operation', on_delete=models.RESTRICT)
    action = models.CharField(max_length=50)
    status = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)