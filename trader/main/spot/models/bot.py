from typing import List
from django.utils import timezone
from django.db import models
from trader.clients import PrivateClient
from trader.main.spot.strategies.strategy_center import SpotStrategyCenter
from .utils.exceptions import BotDoesNotExistsException
from .operation import Operation


class SpotBotManager(models.Manager):
    def find_from_db(self, bot_id):
        try:
            bot = self.get(bot_id=bot_id)
            return bot
        except models.ObjectDoesNotExist:
            raise BotDoesNotExistsException()


class SpotBot(models.Model):
    objects = SpotBotManager()

    # bot_id = models.CharField(max_length=100, unique=True)
    exchange_id = models.CharField(max_length=100)
    credential_id = models.CharField(max_length=100)
    strategy = models.CharField(max_length=100)
    position = models.OneToOneField('SpotPosition', related_name='bot', on_delete=models.RESTRICT)
    created_at = models.CharField(max_length=100, default=timezone.now, blank=True)
    is_active = models.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        super(SpotBot, self).__init__(*args, **kwargs)
        self._strategy_state_data = None
        self._init_requirements()

    def _init_requirements(self):
        self._private_client = PrivateClient(exchange_id=self.exchange_id, credential_id=self.credential_id)
        self._strategy_center = SpotStrategyCenter(exchange_id=self.exchange_id)
        self._strategy_center.set_strategy(self.strategy)

    def reload(self):
        pass

    def get_price_required_symbols(self):
        return self._strategy_center.get_strategy_price_required_symbols()

    def _get_strategy_operations(self):
        return self._strategy_center.get_strategy_operations(self.position, self._strategy_state_data)

    def _execute_strategy_operations(self, operations: List[Operation]):
        for operation in operations:
            if operation.action == 'create':
                if operation.order.type == 'market':
                    if operation.order.side == 'buy':
                        self._private_client.create_market_buy_order_in_quote(
                            symbol=operation.order.symbol,
                            amount_in_qoute=operation.order.amount_in_quote)
                    elif operation.order.side == 'sell':
                        self._private_client.create_market_sell_order(
                            symbol=operation.order.symbol,
                            amount=operation.order.amount)

    def run(self):
        print('in first bot')
        # operations = self._get_strategy_operations()
        # self._execute_strategy_operations(operations)
