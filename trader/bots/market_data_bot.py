from trader.client import client
from pprint import pprint
from trader.global_utils import apply2all_methods, log


@apply2all_methods(log)
class MarketDataBot:

    def get_recent_trades(self, symbol='BTCUSDT'):
        trades = client.get_recent_trades(symbol=symbol)
        pprint(trades)
        return trades

