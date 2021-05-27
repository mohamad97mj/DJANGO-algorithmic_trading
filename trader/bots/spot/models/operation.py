from django.db import models


class Operation(models.Model):
    order = models.OneToOneField('SpotOrder', on_delete=models.RESTRICT, related_name='operation')
    action = models.CharField(max_length=50)
    position = models.ForeignKey('SpotPosition', on_delete=models.RESTRICT, related_name='operations')
    is_executed = models.BooleanField(default=False)
    executed_at = models.DateTimeField(auto_now_add=True)
