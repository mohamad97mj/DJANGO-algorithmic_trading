from django.db import models


class Operation(models.Model):
    order = models.OneToOneField('SpotOrder', related_name='operation', on_delete=models.RESTRICT)
    action = models.CharField(max_length=50)
    position = models.ForeignKey('SpotPosition', related_name='operations', on_delete=models.RESTRICT)
    status = models.CharField(max_length=50)
    executed_at = models.DateTimeField(auto_now_add=True)
