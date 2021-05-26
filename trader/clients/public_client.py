from pprint import pprint
from trader.global_utils import apply2all_methods, log
from trader.exchange.exchange import Exchange
import ccxt.async_support as ccxt


@apply2all_methods(log)
class PublicClient:
    def __init__(self, exchange: Exchange = None):
        self._exchange = exchange

    def get_exchanges(self):
        return ccxt.exchanges

    async def load_markets(self, reload=False):
        return await self._exchange.load_markets(reload=reload)

    async def get_markets(self):
        return await self._exchange.get_markets()

    async def get_market(self, symbol='BTC/USDT'):
        return await self._exchange.get_market(symbol=symbol)

    async def fetch_order_book(self, symbol='BTC/USDT', limit=None):
        return await self._exchange.fetch_order_book(symbol=symbol, limit=limit)


