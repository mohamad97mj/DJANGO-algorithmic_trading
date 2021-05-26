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

    async def fetch_order_book(self, symbol, limit):
        return await self._third_party_exchange.fetch_order_book(symbol=symbol, limit=limit)

    async def fetch_tickers(self, symbols):
        if (self._third_party_exchange.has['fetchTickers']):
            return await self._third_party_exchange.fetch_tickers(symbols=symbols)

    async def fetck_ticker(self, symbol):
        if (self._third_party_exchange.has['fetchTickers']):
            return await self._third_party_exchange.fetch_ticker(symbol=symbol)

    async def fetch_ohlcv(self, symbol, timeframe, since, limit):
        if (self._third_party_exchange.has['fetchOHLCV']):
            return await self._third_party_exchange.fetch_ohlcv(symbol=symbol,
                                                                timeframe=timeframe,
                                                                since=since,
                                                                limit=limit)

    async def close(self):
        await self._third_party_exchange.close()

    def get_time_frames(self):
        return self._third_party_exchange.timeframes
