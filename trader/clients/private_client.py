from pprint import pprint
from trader.global_utils import apply2all_methods, log
from trader.exchange.exchange_factory import ef


@apply2all_methods(log)
class PrivateClient:
    def __init__(self, exchange_id, credential_id):
        self._exchange = ef.create_exchange(exchange_id=exchange_id,
                                            credential_id=credential_id)

    async def fetch_total_balance(self):
        return await self._exchange.fetch_total_balance()

    async def fetch_orders(self, symbol='BTC/USDT'):
        return await self._exchange.fetch_orders()

    async def fetch_order(self, order_id, symbol='BTC/USDT'):
        return await self._exchange.fetch_orders()

    async def fetch_open_orders(self, symbol='BTC/USDT'):
        return await self._exchange.fetch_open_orders(symbol=symbol)

    async def fetch_closed_orders(self):
        return await self._exchange.fetch_closed_orders()

    async def fetch_my_trades(self, symbol='BTC/USDT'):
        return await self._exchange.fetch_my_trades(symbol=symbol)

    async def create_market_buy_order(self, symbol, amount):
        return await self._exchange.create_market_buy_order(symbol=symbol, amount=amount)

    async def create_market_sell_order(self, symbol, amount):
        return await self._exchange.create_market_sell_order(symbol=symbol, amount=amount)

    async def create_limit_buy_order(self, symbol, amount, price):
        return await self._exchange.create_limit_buy_order(symbol=symbol, amount=amount, price=price)

    async def craete_limit_sell_order(self, symbol, amount, price):
        return await self._exchange.create_limit_sell_order(symbol=symbol, amount=amount, price=price)

        # async def create_market_buy_order_in_quote(self, symbol, amount):
        #     return await self._exchange.create_market_buy_order()
