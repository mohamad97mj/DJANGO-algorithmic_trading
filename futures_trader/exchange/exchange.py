import ccxt
from ccxt.base.errors import NetworkError
from global_utils import retry_on_timeout
from trader.utils import apply2all_methods, slash2dash
from .sdk_exchange import SdkExchange


@apply2all_methods(retry_on_timeout(timeout_errors=NetworkError))
class Exchange:
    default_params = {
    }

    def __init__(self,
                 exchange_id,
                 ccxt_exchange: ccxt.Exchange,
                 sdk_exchange: SdkExchange):
        self._exchange_id = exchange_id
        self._ccxt_exchange = ccxt_exchange
        self._sdk_exchange = sdk_exchange

    def get_order(self, order_id):
        return self._sdk_exchange.trade_client.get_order_details(orderId=order_id)

    def create_market_buy_order(self, symbol, leverage, size):
        exchange_order = self._sdk_exchange.trade_client.create_market_order(symbol=symbol,
                                                                             side='buy',
                                                                             lever=leverage,
                                                                             size=size)
        return self.get_order(exchange_order['orderId'])

    def create_market_sell_order(self, symbol, leverage, size):
        exchange_order = self._sdk_exchange.trade_client.create_market_order(symbol=symbol,
                                                                             side='sell',
                                                                             lever=leverage,
                                                                             size=size)
        return self.get_order(exchange_order['orderId'])

    def create_market_buy_order_in_cost(self, symbol, leverage, cost, price):
        size = int((cost * int(leverage)) / price)
        return self.create_market_buy_order(symbol=symbol, leverage=leverage, size=size)

    def create_market_sell_order_in_cost(self, symbol, leverage, cost, price):
        size = int((cost * int(leverage)) / price)
        return self.create_market_sell_order(symbol=symbol, leverage=leverage, size=size)

    def get_all_positions(self):
        return self._sdk_exchange.trade_client.get_all_position()

    def get_position(self, symbol):
        return self._sdk_exchange.trade_client.get_position_details(symbol=symbol)

    def fetch_ticker(self, symbol):
        return self._sdk_exchange.market_client.get_ticker(symbol)

    def get_contracts(self):
        return self._sdk_exchange.market_client.get_contracts_list()

    def get_contract(self, symbol):
        return self._sdk_exchange.market_client.get_contract_detail(symbol=symbol)

    def fetch_status(self):
        return self._ccxt_exchange.fetch_status()

    def load_markets(self, reload):
        return self._ccxt_exchange.load_markets(reload=reload)

    def get_markets(self):
        if not self._ccxt_exchange.markets:
            self._ccxt_exchange.load_markets()

        return self._ccxt_exchange.markets