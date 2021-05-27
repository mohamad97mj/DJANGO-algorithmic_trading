from django.db import models
from trader.exchange import Exchange
from trader.bots.spot.models import SpotPosition
from trader.bots.spot.strategy_center import SpotStrategyCenter


class SpotBot(models.Model):
    credential = models.CharField(max_length=50)

    def __init__(self, exchange: Exchange, position: SpotPosition, strategy_name: str, *args, **kwargs):
        super(SpotBot, self).__init__(*args, **kwargs)
        self._exchange = exchange
        self._position = position
        self.set_strategy(strategy_name)

    def set_strategy(self, strategy_name):
        self._strategy = SpotStrategyCenter.get_strategy(strategy_name, self._position)
        self._strategy.bot = self
        self._strategy.save()

    def run(self):
        pass
