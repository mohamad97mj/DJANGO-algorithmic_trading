from spot_trader.exchange import ef


class PublicClient:
    def __init__(self, exchange_id):
        self._exchange = ef.create_exchange(exchange_id=exchange_id)

        # def get_exchanges(self):
        #     return ccxt.exchanges

    def fetch_status(self):
        return self._exchange.fetch_status()

    def fetch_time(self):
        return self._exchange.fetch_time()

    def load_markets(self, reload=False):
        return self._exchange.load_markets(reload=reload)

    def get_markets(self):
        return self._exchange.get_markets()

    def get_market(self, symbol='BTC/USDT'):
        return self._exchange.get_market(symbol=symbol)

    def get_symbols(self):
        return self._exchange.get_symbols()

    def fetch_order_book(self, symbol='BTC/USDT', limit=None):
        return self._exchange.fetch_order_book(symbol=symbol, limit=limit)

    def fetch_tickers(self, symbols=None):
        if symbols is None:
            symbols = ['BTC/USDT', 'ETH/USDT']

        return self._exchange.fetch_tickers(symbols=symbols)

    def fetch_ticker(self, symbol='BTC/USDT'):
        return self._exchange.fetch_ticker(symbol=symbol)

    def fetch_ohlcv(self, symbol='BTC/USDT', timeframe='1m', since=None, limit=60):
        return self._exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=since, limit=limit)
