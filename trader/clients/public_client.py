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

    def get_markets(self):
        return self._exchange.load_markets()
