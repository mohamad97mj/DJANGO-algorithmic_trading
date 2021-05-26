import ccxt.async_support as ccxt
from ccxt.base.errors import ExchangeError


class Exchange:
    def __init__(self, third_party_exchange: ccxt.Exchange):
        self._third_party_exchange = third_party_exchange

    async def load_markets(self, reload):
        return await self._third_party_exchange.load_markets(reload=reload)

    async def get_markets(self):
        if not self._third_party_exchange.markets:
            await self._third_party_exchange.load_markets()

        return self._third_party_exchange.markets

    async def get_market(self, symbol):
        if not self._third_party_exchange.markets:
            await self._third_party_exchange.load_markets()
        return self._third_party_exchange.market(symbol=symbol)

    async def fetch_order_book(self, symbol):
        return await self._third_party_exchange.fetch_order_book(symbol=symbol)

    async def close(self):
        await self._third_party_exchange.close()
