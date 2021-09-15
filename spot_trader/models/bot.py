import time

from global_utils import my_get_logger
from typing import List, Union
from django.utils import timezone
from django.db import models
from spot_trader.clients import PrivateClient, PublicClient
from global_utils import BotDoesNotExistsException, truncate
from .operation import SpotOperation


class SpotBotManager(models.Manager):
    def find_from_db(self, bot_id):
        try:
            bot = self.get(bot_id=bot_id)
            return bot
        except models.ObjectDoesNotExist:
            raise BotDoesNotExistsException()


class SpotBot(models.Model):
    class Status(models.TextChoices):
        RUNNING = 'running'
        PAUSED = 'paused'
        STOPPED_BY_STOPLOSS = 'stopped_by_stoploss'
        # STOPPED_BY_TRAILING_STOPLOSS = 'stopped_by_trailing_stoploss'
        STOPPED_AFTER_FULL_TARGET = 'stopped_after_full_target'
        STOPPED_MANUALY = 'stopped_manualy'

    objects = SpotBotManager()

    # bot_id = models.CharField(max_length=100, unique=True)
    exchange_id = models.CharField(max_length=100)
    credential_id = models.CharField(max_length=100)
    strategy = models.CharField(max_length=100)
    position = models.OneToOneField('SpotPosition', related_name='bot', on_delete=models.CASCADE)
    total_pnl = models.FloatField(default=0)
    total_pnl_percentage = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(default=Status.RUNNING.value,
                              max_length=50)  # paused, stopped_systematically, stopped_manualy

    def __init__(self, *args, **kwargs):
        super(SpotBot, self).__init__(*args, **kwargs)
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
            self.sell_all_assets()

    def reset(self):
        if not self.strategy == 'manual':
            self.sell_all_assets()

    def sell_all_assets(self):
        logger = my_get_logger()
        markets = self._public_client.get_markets()
        total_balances = self._private_client.fetch_total_balance()
        for currency, balance in total_balances.items():
            symbol = '{}/USDT'.format(currency)
            if symbol in markets:
                if currency != 'USDT' and balance > markets[symbol]['limits']['amount']['min']:
                    ticker = self._public_client.fetch_ticker(symbol)
                    price = ticker['last']
                    if balance * price > markets[symbol]['limits']['cost']['min']:
                        exchange_order = self._private_client.create_market_sell_order(symbol, balance)
                        logger.info(
                            'sold in reset: (symbol: {}, price: {}, amount: {})'.format(
                                symbol,
                                exchange_order['price'],
                                balance))

    def execute_operations(self,
                           operations: List[SpotOperation],
                           test=True):
        for operation in operations:
            position = operation.position
            signal = position.signal
            order = operation.order
            symbol = order.symbol
            price = order.price
            markets = self._public_client.get_markets()
            amount_precision = markets[symbol]['precision']['amount']
            fee = markets[symbol]['maker']
            if operation.action == 'create':
                if order.side == 'buy':
                    step = operation.step
                    if test:
                        exchange_order_id = None
                        timestamp = time.time()
                        buy_amount_in_quote = order.amount_in_quote
                        truncated_buy_amount_before_fee = truncate(
                            buy_amount_in_quote / price,
                            amount_precision)
                        fee_amount = truncated_buy_amount_before_fee * fee
                        cost = truncated_buy_amount_before_fee * price
                        amount = truncated_buy_amount_before_fee - fee_amount
                    else:
                        exchange_order = self._private_client.create_market_buy_order_in_quote(
                            symbol=symbol,
                            amount_in_quote=order.amount_in_quote)
                        timestamp = exchange_order['timestamp']
                        cost = exchange_order['cost']
                        amount = exchange_order['filled']
                        price = exchange_order['price']
                        exchange_order_id = exchange_order['id']

                    step.purchased_amount = amount
                    step.amount_in_quote -= cost
                    step.save()

                    position.holding_amount += amount

                    targets = signal.related_targets
                    for target in targets:
                        target.holding_amount += amount * target.share
                        target.save()

                else:
                    if test:
                        exchange_order_id = None
                        sell_amount = order.amount
                        timestamp = time.time()
                        amount = truncate(sell_amount, amount_precision)
                        sell_amount_in_quote = amount * price
                        fee_amount_in_quote = sell_amount_in_quote * fee
                        pure_sell_amount_in_quote = sell_amount_in_quote - fee_amount_in_quote

                    else:
                        exchange_order = self._private_client.create_market_sell_order(
                            symbol=symbol,
                            amount=order.amount)

                        amount = exchange_order['filled']
                        timestamp = exchange_order['timestamp']
                        pure_sell_amount_in_quote = exchange_order['cost'] - exchange_order['fee']['cost']
                        price = exchange_order['price']
                        exchange_order_id = exchange_order['id']
                    position.released_amount_in_quote += pure_sell_amount_in_quote
                    position.holding_amount -= amount

                    if operation.type == 'take_profit':
                        target = operation.target
                        target.holding_amount -= amount
                        target.released_amount_in_quote = pure_sell_amount_in_quote
                        target.save()

                order.exchange_order_id = exchange_order_id
                order.timestamp = timestamp
                order.status = 'done'
                order.price = price
                order.save()

            operation.status = 'executed'
            operation.save()
            position.save()

    def close_position(self, test):
        if not test:
            exchange_order = self._private_client.create_market_sell_order(symbol=self.position.signal.symbol,
                                                                           amount=self.position.holding_amount)
            self.position.released_amount_in_quote += exchange_order['cost'] - exchange_order['fee']['cost']
            self.position.holding_amount -= exchange_order['filled']
            self.position.save()
