from django.db import models


class Operation:
    order = models.ForeignKey('SpotOrder', on_delete=Restrict)
    action = models.CharField(max_length=50)
    is_done = models.BooleanField()
