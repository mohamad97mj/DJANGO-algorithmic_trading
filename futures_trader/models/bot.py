from global_utils import my_get_logger
from typing import List, Union
from django.utils import timezone
from django.db import models
from futures_trader.clients import PrivateClient, PublicClient
from global_utils import BotDoesNotExistsException, truncate
from .operation import FuturesOperation
from dataclasses import dataclass
from .step import FuturesStep
from .target import FuturesTarget
from .stoploss import FuturesStoploss


class FuturesBotManager(models.Manager):
    def find_from_db(self, bot_id):
        try:
            bot = self.get(bot_id=bot_id)
            return bot
        except models.ObjectDoesNotExist:
            raise BotDoesNotExistsException()


class FuturesBot(models.Model):
    class Status(models.TextChoices):
        RUNNING = 'running'
        PAUSED = 'paused'
        STOPPED_BY_STOPLOSS = 'stopped_by_stoploss'
        STOPPED_BY_TRAILING_STOPLOSS = 'stopped_by_trailing_stoploss'
        STOPPED_AFTER_FULL_TARGET = 'stopped_after_full_target'
        STOPPED_MANUALY = 'stopped_manualy'

    objects = FuturesBotManager()

    # bot_id = models.CharField(max_length=100, unique=True)
    exchange_id = models.CharField(max_length=100)
    credential_id = models.CharField(max_length=100)
    strategy = models.CharField(max_length=100)
    position = models.OneToOneField('FuturesPosition', related_name='bot', on_delete=models.CASCADE)
    final_pnl = models.FloatField(null=True, blank=True)
    final_pnl_percentage = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(default=Status.RUNNING.value,
                              max_length=50)  # paused, stopped_systematically, stopped_manualy

    def __init__(self, *args, **kwargs):
        super(FuturesBot, self).__init__(*args, **kwargs)
        self._private_client = None
        self._public_client = None
        self.strategy_state_data = None

    def init_requirements(self, private_client: PrivateClient, public_client: PublicClient):
        self._private_client = private_client
        self._public_client = public_client

    def set_strategy_state_data(self, strategy_state_data):
        self.strategy_state_data = strategy_state_data

    def ready(self):
        if not self.strategy == 'manual':
            self.close_position()

    def reset(self):
        if not self.strategy == 'manual':
            self.close_position()

    def execute_operations(self,
                           operations: List[FuturesOperation],
                           strategy_state_data,
                           symbol_prices=None,
                           test=True):

        for operation in operations:
            position = operation.position
            signal = position.signal
            order = operation.order
            symbol = order.symbol
            price = symbol_prices[symbol]
            if operation.action == 'create':
                if order.type == 'market':
                    if order.side == 'buy':
                        step = operation.step
                        size = int((step.margin * position.leverage) / price)
                        if test:
                            value = size * price
                            cost = value / order.leverage

                        else:
                            exchange_order = self._private_client.create_market_buy_order(
                                symbol=symbol,
                                leverage=position.leverage,
                                size=size)

                            cost = exchange_order['cost']

                        strategy_state_data.size += size
                        strategy_state_data.available_margin -= cost

                        step.size = size
                        step.cost = cost
                        step.save()

                        position.size += size

                        stoploss = signal.stoploss
                        if stoploss:
                            stoploss.size += size
                            stoploss.save()

                    elif order.side == 'sell':
                        size = order.size
                        stoploss = operation.stoploss
                        if test:
                            value = size * price
                            cost = value / order.leverage

                        else:
                            exchange_order = self._private_client.create_market_sell_order(
                                symbol=symbol,
                                leverage=order.leverage,
                                size=order.size,
                            )
                            cost = exchange_order['cost']

                        strategy_state_data.size -= size
                        strategy_state_data.available_margin += cost

                        stoploss.released_margin = cost
                        stoploss.save()
            position.save()
            operation.status = 'executed'
            operation.save()

    def close_position(self):
        pass
