import time
import pytz
from typing import List
from django.utils import timezone
from django.db import models
from futures_trader.clients import PrivateClient, PublicClient
from global_utils import BotDoesNotExistsException
from .operation import FuturesOperation
from datetime import datetime
from django.conf import settings


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
                           test=True):

        for operation in operations:
            position = operation.position
            order = operation.order
            symbol = order.symbol
            price = order.price
            size = order.size
            if operation.action == 'create':
                if order.side == 'buy':
                    step = operation.step
                    if test:
                        exchange_order_id = None
                        value = size * price
                        filled_value = value
                        timestamp = time.time()

                    else:
                        exchange_order = self._private_client.create_market_buy_order(
                            symbol=symbol,
                            leverage=position.leverage,
                            size=size)
                        exchange_order_id = exchange_order['id']
                        value = exchange_order['value']
                        filled_value = exchange_order['filledValue']
                        timestamp = exchange_order['created_at']

                    strategy_state_data.size += size
                    cost = value / order.leverage
                    strategy_state_data.available_margin -= cost

                    step.cost = cost
                    step.save()

                    position.size += size

                else:
                    if test:
                        exchange_order_id = None
                        value = size * price
                        filled_value = value
                        timestamp = time.time()

                    else:
                        exchange_order = self._private_client.create_market_sell_order(
                            symbol=symbol,
                            leverage=order.leverage,
                            size=order.size,
                        )
                        exchange_order_id = exchange_order['id']
                        value = exchange_order['value']
                        filled_value = exchange_order['filledValue']
                        timestamp = exchange_order['created_at']

                    strategy_state_data.size -= size
                    cost = value / order.leverage
                    strategy_state_data.available_margin += cost

                    position.released_margin = cost

                order.exchange_order_id = exchange_order_id
                order.status = 'done'
                order.value = value
                order.filled_value = filled_value
                order.timestamp = timestamp
                order.created_at = datetime.fromtimestamp(time.time(), tz=pytz.timezone(settings.TIME_ZONE))
                order.save()

            operation.status = 'executed'
            operation.save()
            position.save()

    def close_position(self):
        pass
