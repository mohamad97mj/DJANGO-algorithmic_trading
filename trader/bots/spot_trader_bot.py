from trader.client import client
from pprint import pprint
from trader.global_utils import apply2all_methods, log
from binance import enums


@apply2all_methods(log)
class SpotTraderBot:
    def __init__(self):
        self._client = client

    def get_symbol_all_ordres(self, symbol='BTCUSDT'):
        orders = client.get_all_orders(symbol=symbol)
        print(orders)
        return orders

    def get_dayli_account_snapshot(self):
        info = client.get_account_snapshot(type='SPOT')
        pprint(info)
        return info

    def get_all_orders(self, symbol='BTCUSDT', limit=10):
        orders = client.get_all_orders(symbol=symbol, limit=limit)
        print(orders)
        return orders

    def place_buy_limit_order(self, quantity, price, symbol='BTCUSDT'):
        order = client.order_limit_buy(
            quantity=quantity,
            price=price,
            symbol=symbol,
        )

        print(order)
        return order

    def place_sell_limit_order(self, quantity, price, symbol='BTCUSDT'):
        order = client.order_limit_sell(
            quantity=quantity,
            price=price,
            symbol=symbol,
        )

        print(order)
        return order

    def place_buy_market_order(self, quantity, symbol='BTCUSDT'):
        order = client.order_market_buy(
            quantity=quantity,
            symbol=symbol,
        )
        print(order)
        return order


