from typing import List
from django.utils import timezone
from django.db import models
from trader.clients import PrivateClient, PublicClient
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
        self._private_client = None
        self._strategy_center = None
        self._strategy_state_data = None

    def init_requirements(self, private_client: PrivateClient, public_client: PublicClient):
        self._private_client = private_client
        self._strategy_center = SpotStrategyCenter(public_client=public_client)
        self._strategy_center.set_strategy(self.strategy)

    def reload(self):
        pass

    def get_price_required_symbols(self):
        return self._strategy_center.get_strategy_price_required_symbols()

    def _get_strategy_operations(self, symbol_prices):
        return self._strategy_center.get_strategy_operations(position=self.position,
                                                             strategy_state_data=self._strategy_state_data,
                                                             symbol_prices=symbol_prices)

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

    def run(self, symbol_prices: dict):
        operations = self._get_strategy_operations(symbol_prices=symbol_prices)
        self._execute_strategy_operations(operations)
