from django.db import models
from datetime import datetime


class SpotStrategy(models.Model):
    strategy_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
    bot = models.ForeignKey('SpotBot', related_name='strategies', on_delete=models.RESTRICT, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = datetime.now()
        self.strategy_id = '{}|{}'.format('strategy', now)
