import ccxt
from ccxt.base.errors import NetworkError
from global_utils import retry_on_timeout, apply2all_methods, slash2dash
from .sdk_exchange import SdkExchange


@apply2all_methods(retry_on_timeout(timeout_errors=NetworkError))
class Exchange:
    default_params = {
    }

    def __init__(self,
                 exchange_id,
                 ccxt_exchange: ccxt.Exchange,
                 sdk_exchange: SdkExchange):  # pb stands for python binance
        self._exchange_id = exchange_id
        self._ccxt_exchange = ccxt_exchange
        self._sdk_exchange = sdk_exchange

    def fetch_status(self):
        return self._ccxt_exchange.fetch_status()

    def fetch_time(self):
        return self._ccxt_exchange.fetch_time()

    def load_markets(self, reload):
        return self._ccxt_exchange.load_markets(reload=reload)

    def get_markets(self):
        if not self._ccxt_exchange.markets:
            self._ccxt_exchange.load_markets()

        return self._ccxt_exchange.markets

    def get_market(self, symbol):
        if not self._ccxt_exchange.markets:
            self._ccxt_exchange.load_markets()
        return self._ccxt_exchange.market(symbol=symbol)

    def get_symbols(self):
        if not self._ccxt_exchange.markets:
            self._ccxt_exchange.load_markets()
        return self._ccxt_exchange.symbols

    def fetch_order_book(self, symbol, limit):
        return self._ccxt_exchange.fetch_order_book(symbol=symbol, limit=limit)

    def fetch_tickers(self, symbols):
        if self._ccxt_exchange.has['fetchTickers']:
            return self._ccxt_exchange.fetch_tickers(symbols=symbols)

    def fetch_ticker(self, symbol):
        if self._ccxt_exchange.has['fetchTickers']:
            return self._ccxt_exchange.fetch_ticker(symbol=symbol)

    def fetch_ohlcv(self, symbol, timeframe, since, limit):
        if self._ccxt_exchange.has['fetchOHLCV']:
            return self._ccxt_exchange.fetch_ohlcv(symbol=symbol,
                                                   timeframe=timeframe,
                                                   since=since,
                                                   limit=limit)

    def get_timeframes(self):
        return self._ccxt_exchange.timeframes

    def fetch_total_balance(self):
        if self._exchange_id == 'binance':
            return self._ccxt_exchange.fetch_total_balance()
        elif self._exchange_id == 'kucoin':
            return self._sdk_exchange.user_client.get_account_list()

    def fetch_balance(self):
        return self._ccxt_exchange.fetch_balance()

    def fetch_orders(self):
        return self._ccxt_exchange.fetch_orders()

    def fetch_order(self, order_id):
        return self._ccxt_exchange.fetch_order(order_id)

    def fetch_open_orders(self, symbol):
        return self._ccxt_exchange.fetch_open_orders(symbol=symbol)

    def fetch_closed_orders(self):
        return self._ccxt_exchange.fetch_closed_orders()

    def fetch_my_trades(self, symbol):
        return self._ccxt_exchange.fetch_my_trades(symbol=symbol)

    def create_market_buy_order(self, symbol, amount):
        exchange_order = self._ccxt_exchange.create_market_buy_order(symbol=symbol, amount=amount)
        if self._exchange_id == 'kucoin':
            exchange_order = self.fetch_order(exchange_order['id'])
        return exchange_order

    def create_market_buy_order_in_quote(self, symbol, amount_in_quote):
        if self._exchange_id == 'binance':
            return self._ccxt_exchange.create_order(symbol=symbol,
                                                    type='market',
                                                    side='buy',
                                                    amount=amount_in_quote,
                                                    price=1,
                                                    params=self.default_params)
        elif self._exchange_id == 'kucoin':
            exchange_order = self._sdk_exchange.trade_client.create_market_order(symbol=slash2dash(symbol),
                                                                                 side='buy',
                                                                                 funds=str(amount_in_quote))

            return self.fetch_order(exchange_order['orderId'])

    def create_market_sell_order(self, symbol, amount):
        exchange_order = self._ccxt_exchange.create_market_sell_order(symbol=symbol, amount=amount)
        if self._exchange_id == 'kucoin':
            exchange_order = self.fetch_order(exchange_order['id'])
        return exchange_order

    def create_limit_buy_order(self, symbol, amount, price):
        return self._ccxt_exchange.create_limit_buy_order(symbol=symbol, amount=amount, price=price)

    def create_limit_sell_order(self, symbol, amount, price):
        return self._ccxt_exchange.create_limit_sell_order(symbol=symbol, amount=amount, price=price)

    def close(self):
        self._ccxt_exchange.close()
