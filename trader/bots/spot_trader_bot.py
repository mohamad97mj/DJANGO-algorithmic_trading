from trader.client import client
from pprint import pprint
from trader.global_utils import apply2all_methods, log


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
