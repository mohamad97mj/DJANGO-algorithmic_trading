import ccxt.async_support as ccxt


class Exchange:
    def __init__(self, third_party_exchange: ccxt.Exchange):
        self._third_party_exchange = third_party_exchange

    async def load_markets(self, reload):
        markets = await self._third_party_exchange.load_markets(reload=reload)
        return markets

    def get_markets(self):
        return self._third_party_exchange.markets

    async def close(self):
        await self._third_party_exchange.close()
