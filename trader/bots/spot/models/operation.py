from django.db import models


class Operation(models.Model):
    operation_id = models.CharField(max_length=100, unique=True)
    order = models.OneToOneField('SpotOrder', related_name='operation', on_delete=models.RESTRICT)
    action = models.CharField(max_length=50)
    position = models.ForeignKey('SpotPosition', related_name='operations', on_delete=models.RESTRICT)
    status = models.CharField(max_length=50, blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)
