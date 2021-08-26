from global_utils import my_get_logger
from typing import List, Union
from django.utils import timezone
from django.db import models
from trader.clients import PrivateClient, PublicClient
from trader.utils import truncate
from .utils.exceptions import BotDoesNotExistsException
from .operation import SpotOperation
from dataclasses import dataclass
from .step import SpotStep
from .target import SpotTarget
from .stoploss import SpotStoploss


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
        STOPPED_BY_TRAILING_STOPLOSS = 'stopped_by_trailing_stoploss'
        STOPPED_AFTER_FULL_TARGET = 'stopped_after_full_target'
        STOPPED_MANUALY = 'stopped_manualy'

    @dataclass
    class ExchangeOrderData:
        side: str
        symbol: str
        cost: float
        fee: float
        amount: float
        related_setup: Union[SpotStep, SpotTarget, SpotStoploss]  # could be step_id, target_id or stoploss_id

    objects = SpotBotManager()

    # bot_id = models.CharField(max_length=100, unique=True)
    exchange_id = models.CharField(max_length=100)
    credential_id = models.CharField(max_length=100)
    strategy = models.CharField(max_length=100)
    position = models.OneToOneField('SpotPosition', related_name='bot', on_delete=models.CASCADE)
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

    def execute_operations(self, operations: List[SpotOperation], test=True, symbol_prices=None):
        exchange_orders_data = []
        for operation in operations:
            exchange_order_data = None
            if operation.action == 'create':
                if operation.order.type == 'market':

                    symbol = operation.order.symbol
                    markets = self._public_client.get_markets()
                    amount_precision = markets[symbol]['precision']['amount']
                    fee = markets[symbol]['maker']
                    deviation = 0.0001

                    if operation.order.side == 'buy':
                        related_setup = operation.step
                        if test:
                            buy_amount_in_quote = operation.order.amount_in_quote
                            buy_price = symbol_prices[symbol]
                            truncated_buy_amount_before_fee = truncate(
                                buy_amount_in_quote / (buy_price * (1 + deviation)),
                                amount_precision)
                            fee_amount = truncated_buy_amount_before_fee * fee
                            real_buy_amount_in_quote = truncated_buy_amount_before_fee * buy_price
                            exchange_order_data = SpotBot.ExchangeOrderData(side='buy',
                                                                            symbol=symbol,
                                                                            cost=real_buy_amount_in_quote,
                                                                            amount=truncated_buy_amount_before_fee,
                                                                            fee=fee_amount,
                                                                            related_setup=related_setup)
                            pure_buy_amount = truncated_buy_amount_before_fee - fee_amount
                            operation.step.purchased_amount = pure_buy_amount
                        else:
                            exchange_order = self._private_client.create_market_buy_order_in_quote(
                                symbol=symbol,
                                amount_in_qoute=operation.order.amount_in_quote)
                            exchange_order_data = SpotBot.ExchangeOrderData(side='buy',
                                                                            symbol=symbol,
                                                                            cost=exchange_order['cost'],
                                                                            amount=exchange_order['amount'],
                                                                            fee=exchange_order['fee']['cost'],
                                                                            related_setup=related_setup)

                            pure_buy_amount = exchange_order['amount'] - exchange_order['fee']['cost']
                            operation.step.purchased_amount = pure_buy_amount
                        operation.step.save()

                    elif operation.order.side == 'sell':
                        related_setup = operation.stoploss if operation.type == 'stoploss_triggered' else operation.target
                        if test:

                            sell_amount = operation.order.amount
                            sell_price = symbol_prices[symbol]
                            truncated_sell_amount_before_fee = truncate(sell_amount, amount_precision)
                            sell_amount_in_quote = truncated_sell_amount_before_fee * (sell_price * (1 - deviation))
                            fee_amount_in_quote = sell_amount_in_quote * fee
                            exchange_order_data = SpotBot.ExchangeOrderData(side='sell',
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
                            exchange_order_data = SpotBot.ExchangeOrderData(side='sell',
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
        self.sell_all_assets()
