from django.db import models
from django.utils import timezone


class SpotOperation(models.Model):
    # operation_id = models.CharField(max_length=100, unique=True)
    order = models.OneToOneField('SpotOrder', related_name='operation', on_delete=models.RESTRICT)
    action = models.CharField(max_length=50)
    position = models.ForeignKey('SpotPosition', related_name='operations', null=True, blank=True,
                                 on_delete=models.CASCADE)
    status = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    executed_at = models.CharField(max_length=100, blank=True)
