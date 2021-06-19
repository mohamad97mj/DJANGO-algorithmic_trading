from trader.global_utils import apply2all_methods, log
from trader.exchange import ef


@apply2all_methods(log)
class PublicClient:
    def __init__(self, exchange_id):
        self._exchange = ef.create_exchange(exchange_id=exchange_id)

        # def get_exchanges(self):
        #     return ccxt.exchanges

    def load_markets(self, reload=False):
        return self._exchange.load_markets(reload=reload)

    def get_markets(self):
        return self._exchange.get_markets()

    def get_market(self, symbol='BTC/USDT'):
        return self._exchange.get_market(symbol=symbol)

    def fetch_order_book(self, symbol='BTC/USDT', limit=None):
        return self._exchange.fetch_order_book(symbol=symbol, limit=limit)

    def fetch_tickers(self, symbols=None):
        if symbols is None:
            symbols = ['BTC/USDT', 'ETH/USDT']

        return self._exchange.fetch_tickers(symbols=symbols)

    def fetch_ticker(self, symbol='BTC/USDT'):
        return self._exchange.fetck_ticker(symbol=symbol)

    def fetch_ohlcv(self, symbol='BTC/USDT', timeframe='1m', since=None, limit=None):
        if not limit:
            limit = get_appropriate_limit(timeframe)
        return self._exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=since, limit=limit)

    def fetch_status(self):
        return self._exchange.fetch_status()


def get_appropriate_limit(timeframe):
    return int({
                   '1m': 24 * 60,
                   '3m': (24 * 60) / 3,
                   '5m': (24 * 60) / 5,
                   '15m': (24 * 60) / 15,
                   '30m': (24 * 60) / 30,
                   '1h': 24,
                   '2h': 12,
                   '4h': 6,
                   '6h': 4,
                   '8h': 3,
               }[timeframe])
