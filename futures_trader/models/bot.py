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
        CREATED = 'created'
        WAITING = 'waiting'
        RUNNING = 'running'
        PAUSED = 'paused'
        STOPPED_BY_STOPLOSS = 'stopped_by_stoploss'
        STOPPED_BY_TRAILING_STOPLOSS = 'stopped_by_trailing_stoploss'
        STOPPED_AFTER_FULL_TARGET = 'stopped_after_full_target'
        STOPPED_MANUALLY = 'stopped_manually'
        STOPPED = 'stopped'

    objects = FuturesBotManager()

    # bot_id = models.CharField(max_length=100, unique=True)
    exchange_id = models.CharField(max_length=100)
    credential_id = models.CharField(max_length=100)
    strategy = models.CharField(max_length=100)
    position = models.OneToOneField('FuturesPosition', related_name='bot', on_delete=models.CASCADE)
    total_pnl = models.FloatField(null=True, blank=True)
    total_pnl_percentage = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(default=Status.RUNNING.value,
                              max_length=50)  # paused, stopped_systematically, stopped_manually

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
        pass

    def reset(self):
        pass

    def execute_operations(self,
                           operations: List[FuturesOperation],
                           strategy_state_data,
                           test=True):

        for operation in operations:

            position = operation.position
            signal = position.signal
            order = operation.order
            symbol = order.symbol
            price = order.price
            multiplier = self._public_client.get_contract(symbol)['multiplier']
            size = int(order.size / multiplier) * multiplier
            if operation.action == 'create':
                if False:
                    exchange_order_id = None
                    value = size * price
                    filled_value = value
                    timestamp = time.time()

                else:
                    if order.type == 'market':
                        exchange_order = self._private_client.create_market_order(
                            symbol=symbol,
                            leverage=signal.leverage,
                            side=order.side,
                            size=size,
                            multiplier=multiplier,
                        )
                    else:
                        exchange_order = self._private_client.create_limit_order(
                            symbol=symbol,
                            leverage=signal.leverage,
                            side=order.side,
                            size=size,
                            price=order.price,
                            multiplier=multiplier,
                        )

                    exchange_order_id = exchange_order['id']
                    value = float(exchange_order['value'])
                    filled_value = float(exchange_order['filledValue'])
                    timestamp = exchange_order['createdAt']

                cost = value / order.leverage

                if operation.type == 'step':
                    strategy_state_data.available_margin -= cost
                    step = operation.step
                    step.purchased_size = size
                    step.cost = cost
                    step.save()
                    position.purchased_value += value
                    position.holding_size += size
                    remaining_size = size

                    targets = signal.related_targets
                    for i in range(len(targets)):
                        target = targets[i]
                        shared_size = size * target.share
                        target.holding_size += remaining_size if i == len(targets) - 1 else shared_size
                        remaining_size -= shared_size
                        target.save()
                else:
                    target = operation.target
                    target.holding_size -= size
                    target.save()
                    position.holding_size -= size
                    position.released_margin += value

                order.exchange_order_id = exchange_order_id
                order.size = size
                order.status = 'done'
                order.value = value
                order.filled_value = filled_value
                order.timestamp = timestamp
                order.created_at = datetime.fromtimestamp(time.time(), tz=pytz.timezone(settings.TIME_ZONE))
                order.save()

            operation.status = 'executed'
            operation.save()
            signal.save()
            position.save()

    def close_position(self, test):
        if not test:
            self._private_client.close_position(self.position.signal.symbol)

    def is_risky(self):
        return not self.position.signal.stoploss.is_trailed if self.position.signal.stoploss else True
