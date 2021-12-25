from django.utils import timezone
from django.db import models


class FuturesSignal(models.Model):
    # signal_id = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=50)
    side = models.CharField(max_length=10)
    leverage = models.IntegerField()
    stoploss = models.OneToOneField('FuturesStoploss', related_name='signal', null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    setup_mode = models.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        super(FuturesSignal, self).__init__(*args, **kwargs)
        self.related_steps = []
        self.related_targets = []
        self._init_relations()

    def _init_relations(self):
        self._init_related_steps()
        self._init_related_targets()

    def _init_related_steps(self):
        steps = list(self.steps.order_by('entry_price'))
        if steps:
            if steps[0].entry_price == -1:
                steps.append(steps.pop(0))
            self.related_steps = steps

    def _init_related_targets(self):
        targets = list(self.targets.order_by('tp_price'))
        if targets:
            self.related_targets = targets
