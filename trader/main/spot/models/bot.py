from global_utils import my_get_logger
from typing import List
from django.utils import timezone
from django.db import models
from trader.clients import PrivateClient, PublicClient
from trader.utils import truncate
from .utils.exceptions import BotDoesNotExistsException
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
        STOPPED_SYSTEMATICALLY = 'stopped_systematically'
        STOPPED_MANUALY = 'stopped_manualy'

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

    def execute_operations(self, operations: List[SpotOperation], test=False, symbol_prices=None):
        exchange_orders = []
        for operation in operations:
            if operation.action == 'create':
                if operation.order.type == 'market':

                    symbol = operation.order.symbol
                    markets = self._public_client.get_markets()
                    amount_precision = markets[symbol]['precision']['amount']
                    fee = markets[symbol]['maker']
                    deviation = 0.0001

                    if operation.order.side == 'buy':
                        if test:
                            buy_amount_in_quote = operation.order.amount_in_quote
                            buy_price = symbol_prices[symbol]
                            truncated_buy_amount_before_fee = truncate(
                                buy_amount_in_quote / (buy_price * (1 + deviation)),
                                amount_precision)
                            fee_amount = truncated_buy_amount_before_fee * fee
                            real_buy_amount_in_quote = truncated_buy_amount_before_fee * buy_price
                            exchange_order = {'side': 'buy',
                                              'symbol': symbol,
                                              'cost': real_buy_amount_in_quote,
                                              'amount': truncated_buy_amount_before_fee,
                                              'fee': {'cost': fee_amount}}
                            pure_buy_amount = truncated_buy_amount_before_fee - fee_amount
                            operation.step.purchased_amount = pure_buy_amount
                        else:
                            exchange_order = self._private_client.create_market_buy_order_in_quote(
                                symbol=symbol,
                                amount_in_qoute=operation.order.amount_in_quote)
                            pure_buy_amount = exchange_order['amount'] - exchange_order['fee']['cost']
                            operation.step.purchased_amount = pure_buy_amount
                        operation.step.save()

                    elif operation.order.side == 'sell':
                        if test:

                            sell_amount = operation.order.amount
                            sell_price = symbol_prices[symbol]
                            truncated_sell_amount_before_fee = truncate(sell_amount, amount_precision)
                            sell_amount_in_quote = truncated_sell_amount_before_fee * (sell_price * (1 - deviation))
                            fee_amount_in_quote = sell_amount_in_quote * fee

                            exchange_order = {
                                'side': 'sell',
                                'symbol': symbol,
                                'cost': sell_amount_in_quote,
                                'fee': {'cost': fee_amount_in_quote},
                                'amount': truncated_sell_amount_before_fee
                            }
                            pure_sell_amount_in_quote = sell_amount_in_quote - fee_amount_in_quote
                            operation.target.released_amount_in_quote = pure_sell_amount_in_quote
                        else:
                            exchange_order = self._private_client.create_market_sell_order(
                                symbol=symbol,
                                amount=operation.order.amount)
                            pure_sell_amount_in_quote = exchange_order['cost'] - exchange_order['fee']['cost']
                            operation.target.released_amount_in_quote = pure_sell_amount_in_quote
                        operation.target.save()

            logger = my_get_logger()
            logger.info('exchange_order: {}'.format(exchange_order))
            exchange_orders.append(exchange_order)

        return exchange_orders

    def close_position(self):
        self.sell_all_assets()
