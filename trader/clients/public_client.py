from pprint import pprint
from trader.global_utils import apply2all_methods, log
from trader.exchange.exchange import Exchange
# import ccxt.async_support as ccxt
from trader.exchange import ef


@apply2all_methods(log)
class PublicClient:
    def __init__(self, exchange_id):
        self._exchange = ef.create_exchange(exchange_id=exchange_id)

    # def get_exchanges(self):
    #     return ccxt.exchanges

    async def load_markets(self, reload=False):
        return await self._exchange.load_markets(reload=reload)

    async def get_markets(self):
        return await self._exchange.get_markets()

    async def get_market(self, symbol='BTC/USDT'):
        return await self._exchange.get_market(symbol=symbol)

    async def fetch_order_book(self, symbol='BTC/USDT', limit=None):
        return await self._exchange.fetch_order_book(symbol=symbol, limit=limit)

    async def fetch_tickers(self, symbols=None):
        if symbols is None:
            symbols = ['BTC/USDT', 'ETH/USDT']

        return await self._exchange.fetch_tickers(symbols=symbols)

    async def fetch_ticker(self, symbol='BTC/USDT'):
        return await self._exchange.fetck_ticker(symbol=symbol)

    async def fetch_ohlcv(self, symbol='BTC/USDT', timeframe='1m', since=None, limit=None):
        if not limit:
            limit = get_appropriate_limit(timeframe)
        return await self._exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=since, limit=limit)

    async def fetch_status(self):
        return await self._exchange.fetch_status()


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
