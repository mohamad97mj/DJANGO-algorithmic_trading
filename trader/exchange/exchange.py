import ccxt.async_support as ccxt
from ccxt.base.errors import ExchangeError


class Exchange:
    def __init__(self, ccxt_exchange: ccxt.Exchange):
        self._ccxt_exchange = ccxt_exchange

    async def load_markets(self, reload):
        return await self._ccxt_exchange.load_markets(reload=reload)

    async def get_markets(self):
        if not self._ccxt_exchange.markets:
            await self._ccxt_exchange.load_markets()

        return self._ccxt_exchange.markets

    async def get_market(self, symbol):
        if not self._ccxt_exchange.markets:
            await self._ccxt_exchange.load_markets()
        return self._ccxt_exchange.market(symbol=symbol)

    async def fetch_order_book(self, symbol, limit):
        return await self._ccxt_exchange.fetch_order_book(symbol=symbol, limit=limit)

    async def fetch_tickers(self, symbols):
        if (self._ccxt_exchange.has['fetchTickers']):
            return await self._ccxt_exchange.fetch_tickers(symbols=symbols)

    async def fetck_ticker(self, symbol):
        if (self._ccxt_exchange.has['fetchTickers']):
            return await self._ccxt_exchange.fetch_ticker(symbol=symbol)

    async def fetch_ohlcv(self, symbol, timeframe, since, limit):
        if (self._ccxt_exchange.has['fetchOHLCV']):
            return await self._ccxt_exchange.fetch_ohlcv(symbol=symbol,
                                                         timeframe=timeframe,
                                                         since=since,
                                                         limit=limit)

    def get_timeframes(self):
        return self._ccxt_exchange.timeframes

    async def fetch_total_balance(self):
        return await self._ccxt_exchange.fetch_total_balance()

    async def fetch_balance(self, symbol='BTC/USDT'):
        return await self._ccxt_exchange.fetch_total_balance()[symbol]

    async def fetch_orders(self):
        return await self._ccxt_exchange.fetch_orders()

    async def fetch_open_orders(self, symbol):
        return await self._ccxt_exchange.fetch_open_orders(symbol=symbol)

    async def fetch_closed_orders(self):
        return await self._ccxt_exchange.fetch_closed_orders()

    async def fetch_my_trades(self, symbol):
        return await self._ccxt_exchange.fetch_my_trades(symbol=symbol)

    async def create_market_buy_order(self, symbol, amount):
        return await self._ccxt_exchange.create_market_buy_order(symbol=symbol, amount=amount)

    async def create_market_sell_order(self, symbol, amount):
        return await self._ccxt_exchange.create_market_sell_order(symbol=symbol, amount=amount)

    async def create_limit_buy_order(self, symbol, amount, price):
        return await self._ccxt_exchange.create_limit_buy_order(symbol=symbol, amount=amount, price=price)

    async def create_limit_sell_order(self, symbol, amount, price):
        return await self._ccxt_exchange.create_limit_sell_order(symbol=symbol, amount=amount, price=price)

    async def close(self):
        await self._ccxt_exchange.close()
