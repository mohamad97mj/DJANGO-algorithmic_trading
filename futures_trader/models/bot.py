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

    @dataclass
    class ExchangeOrderData:
        side: str
        symbol: str
        size: float
        value: float
        cost: float
        fee: float
        related_setup: Union[FuturesStep, FuturesTarget, FuturesStoploss]  # could be step_id, target_id or stoploss_id

    objects = FuturesBotManager()

    # bot_id = models.CharField(max_length=100, unique=True)
    exchange_id = models.CharField(max_length=100)
    credential_id = models.CharField(max_length=100)
    strategy = models.CharField(max_length=100)
    position = models.OneToOneField('FuturesPosition', related_name='bot', on_delete=models.CASCADE)
    total_pnl = models.FloatField(default=0)
    total_pnl_percentage = models.FloatField(default=0)
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

    def execute_operations(self, operations: List[FuturesOperation], symbol_prices=None, test=True):
        exchange_orders_data = []
        for operation in operations:
            exchange_order_data = None
            position = operation.position
            order = operation.order
            if operation.action == 'create':
                if order.type == 'market':

                    symbol = order.symbol
                    markets = self._public_client.get_markets()
                    amount_precision = markets[symbol]['precision']['amount']
                    fee = markets[symbol]['maker']

                    if operation.order.side == 'buy':
                        step = operation.step
                        buy_price = symbol_prices[symbol]
                        size = int((order.cost * position.leverage) / buy_price)
                        if test:
                            value = size * buy_price
                            cost = value / order.leverage
                            fee = cost * fee
                            exchange_order_data = FuturesBot.ExchangeOrderData(side='buy',
                                                                               symbol=symbol,
                                                                               size=size,
                                                                               value=value,
                                                                               cost=cost,
                                                                               fee=fee,
                                                                               related_setup=step)
                            step = operation.step
                            step.size = size
                            step.purchased_value = value
                            step.cost = cost
                        else:
                            exchange_order = self._private_client.create_market_buy_order(
                                symbol=symbol,
                                leverage=position.leverage,
                                size=size)

                            exchange_order_data = FuturesBot.ExchangeOrderData(side='buy',
                                                                               symbol=symbol,
                                                                               size=exchange_order['size'],
                                                                               value=exchange_order['value'],
                                                                               cost=exchange_order['cost'],
                                                                               fee=exchange_order['fee']['cost'],
                                                                               related_setup=related_setup)

                            pure_buy_amount = exchange_order['amount'] - exchange_order['fee']['cost']
                            operation.step.purchased_amount = pure_buy_amount
                        step.save()

                elif operation.order.side == 'sell':
                    related_setup = operation.stoploss if operation.type == 'stoploss_triggered' else operation.target
                    if test:

                        sell_amount = operation.order.amount
                        sell_price = symbol_prices[symbol]
                        truncated_sell_amount_before_fee = truncate(sell_amount, amount_precision)
                        sell_amount_in_quote = truncated_sell_amount_before_fee * (sell_price * (1 - deviation))
                        fee_amount_in_quote = sell_amount_in_quote * fee
                        exchange_order_data = FuturesBot.ExchangeOrderData(side='sell',
                                                                           symbol=symbol,
                                                                           cost=sell_amount_in_quote,
                                                                           fee=fee_amount_in_quote,
                                                                           amount=truncated_sell_amount_before_fee,
                                                                           related_setup=related_setup)

                        pure_sell_amount_in_quote = sell_amount_in_quote - fee_amount_in_quote
                        related_setup.released_amount_in_quote = pure_sell_amount_in_quote

                    else:
                        exchange_order = self._private_client.create_market_sell_order(
                            symbol=symbol,
                            amount=operation.order.amount)
                        exchange_order_data = FuturesBot.ExchangeOrderData(side='sell',
                                                                           symbol=symbol,
                                                                           cost=exchange_order['cost'],
                                                                           fee=exchange_order['fee']['cost'],
                                                                           amount=exchange_order['amount'],
                                                                           related_setup=related_setup)
                        pure_sell_amount_in_quote = exchange_order['cost'] - exchange_order['fee']['cost']
                        related_setup.released_amount_in_quote = pure_sell_amount_in_quote
                        related_setup.save()

        logger = my_get_logger()
        logger.info('exchange_order: {}'.format(exchange_order_data))
        exchange_orders_data.append(exchange_order_data)

        return exchange_orders_data


def close_position(self):
    pass
