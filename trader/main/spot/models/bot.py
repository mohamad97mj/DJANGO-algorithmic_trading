from global_utils import my_get_logger
from typing import List
from django.utils import timezone
from django.db import models
from trader.clients import PrivateClient, PublicClient
from trader.main.spot.strategies.strategy_center import SpotStrategyCenter
from trader.utils import truncate
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
    position = models.OneToOneField('SpotPosition', related_name='bot', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, blank=True)
    is_active = models.BooleanField(default=True)

    def __init__(self, *args, **kwargs):
        super(SpotBot, self).__init__(*args, **kwargs)
        self._private_client = None
        self._public_client = None
        self._strategy_developer = None
        self._strategy_state_data = None

    def init_requirements(self, private_client: PrivateClient, public_client: PublicClient):
        self._private_client = private_client
        self._public_client = public_client
        self._strategy_developer = SpotStrategyCenter.get_strategy_developer(self.strategy, public_client)
        self._strategy_state_data = self._strategy_developer.init_strategy_state_data(position=self.position)

    def ready(self):
        if not self.strategy == 'manual':
            self.sell_all_assets()

    def reset(self):
        if not self.strategy == 'manual':
            self.sell_all_assets()
            self._strategy_state_data = self._strategy_developer.reset(self.position)

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

    def get_price_required_symbols(self):
        return self._strategy_developer.get_strategy_symbols(self.position)

    def _get_strategy_operations(self, symbol_prices):
        return self._strategy_developer.get_operations(position=self.position,
                                                       strategy_state_data=self._strategy_state_data,
                                                       symbol_prices=symbol_prices)

    def _execute_operations(self, operations: List[Operation], test=False
                            , symbol_prices=None):
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

                        else:
                            exchange_order = self._private_client.create_market_buy_order_in_quote(
                                symbol=symbol,
                                amount_in_qoute=operation.order.amount_in_quote)

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
                        else:
                            exchange_order = self._private_client.create_market_sell_order(
                                symbol=symbol,
                                amount=operation.order.amount)

            logger = my_get_logger()
            logger.info('exchange_order: {}'.format(exchange_order))
            self._strategy_developer.update_strategy_state_data(exchange_order, self._strategy_state_data)

    def run(self, symbol_prices: dict):
        operations = self._get_strategy_operations(symbol_prices=symbol_prices)
        self._execute_operations(operations, test=True, symbol_prices=symbol_prices)

    def run_strategy_command(self, command, *args, **kwargs):
        strategy_method = getattr(self._strategy_developer, command)
        print(strategy_method(*args, **kwargs))

    def close_position(self):
        pass
