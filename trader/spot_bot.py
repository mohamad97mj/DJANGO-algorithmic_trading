from .client import client
from pprint import pprint


class SpotBotClient:
    def __init__(self):
        self._client = client

    def get_exchange_info(self):
        res = client.get_exchange_info()
        pprint(res)
        return res

    def get_symbol_all_ordres(self, symbol='BTCUSDT'):
        orders = client.get_all_orders(symbol=symbol)
        print(orders)
        return orders
