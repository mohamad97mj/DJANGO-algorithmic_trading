import ccxt
from ccxt.base.errors import NetworkError
from global_utils import retry_on_timeout
from trader.utils import apply2all_methods


@apply2all_methods(retry_on_timeout(timeout_errors=NetworkError))
class Exchange:
    default_params = {
        'recvWindow': 10000
    }

    def __init__(self, ccxt_exchange: ccxt.Exchange, pb_exchange):  # pb stands for python binance
        self._ccxt_exchange = ccxt_exchange
        self._pb_exchange = pb_exchange

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
        return self._ccxt_exchange.fetch_total_balance()

    def fetch_balance(self, symbol='BTC/USDT'):
        return self._ccxt_exchange.fetch_total_balance()[symbol]

    def fetch_orders(self):
        return self._ccxt_exchange.fetch_orders()

    def fetch_open_orders(self, symbol):
        return self._ccxt_exchange.fetch_open_orders(symbol=symbol)

    def fetch_closed_orders(self):
        return self._ccxt_exchange.fetch_closed_orders()

    def fetch_my_trades(self, symbol):
        return self._ccxt_exchange.fetch_my_trades(symbol=symbol)

    def create_market_buy_order(self, symbol, amount):
        return self._ccxt_exchange.create_market_buy_order(symbol=symbol, amount=amount)

    def create_market_buy_order_in_quote(self, symbol, amount, price):
        return self._ccxt_exchange.create_order(symbol=symbol, type='market', side='buy', amount=amount, price=price,
                                                params=self.default_params)

    def create_market_sell_order(self, symbol, amount):
        return self._ccxt_exchange.create_market_sell_order(symbol=symbol, amount=amount)

    def create_limit_buy_order(self, symbol, amount, price):
        return self._ccxt_exchange.create_limit_buy_order(symbol=symbol, amount=amount, price=price)

    def create_limit_sell_order(self, symbol, amount, price):
        return self._ccxt_exchange.create_limit_sell_order(symbol=symbol, amount=amount, price=price)

    def close(self):
        self._ccxt_exchange.close()
