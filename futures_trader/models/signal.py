from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import ArrayField


class FuturesSignal(models.Model):
    # signal_id = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=50)
    stoploss = models.OneToOneField('FuturesStoploss', related_name='signal', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    step_share_set_mode = models.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        super(FuturesSignal, self).__init__(*args, **kwargs)
        self.related_steps = []
        self.related_targets = []
        self._init_relations()

    def _init_relations(self):
        self._init_related_steps()
        self._init_related_targets()

    def _init_related_steps(self):
        steps = self.steps.all()
        if steps:
            self.related_steps = list(steps)

    def _init_related_targets(self):
        targets = self.targets.all()
        if targets:
            self.related_targets = list(targets)