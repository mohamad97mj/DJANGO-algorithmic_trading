from django.db import models
from trader.exchange import Exchange
from .position import SpotPosition
from .strategy import SpotStrategy
from .operation import Operation
from trader.bots.spot.strategy_center import SpotStrategyCenter
from .exceptions import BotDoesNotExistsException


class SpotBotManager(models.Manager):
    def _find_from_db(self, id):
        try:
            bot = self.get(id=id)
            return bot
        except models.ObjectDoesNotExist:
            raise BotDoesNotExistsException()


class SpotBot(models.Model):
    objects = SpotBotManager()

    bot_id = models.CharField(max_length=100, unique=True)
    credential = models.CharField(max_length=50)
    current_strategy_id = models.BigIntegerField()

    def __init__(self, exchange: Exchange, position: SpotPosition, strategy_name: str, *args, **kwargs):
        super(SpotBot, self).__init__(*args, **kwargs)
        self._exchange = exchange
        self._current_strategy = None
        self.set_strategy(strategy_name, position)

    def set_strategy(self, strategy_name, position):
        self.current_strategy = SpotStrategyCenter.get_strategy(strategy_name, position)
        self.current_strategy.bot = self
        self.current_strategy.save()
        self.current_strategy_id = self.current_strategy.id
        self.save()

    def reload_bot(self):
        self._reload_strategy()
        self._reload_operations()

    def _reload_strategy(self):
        self.current_strategy: SpotStrategy = self.strategies.get(id=self.current_strategy_id)

    def _reload_operations(self):
        self._operations: SpotOperation = self.current_strategy.position.operations.all()

    def run(self):
        pass
