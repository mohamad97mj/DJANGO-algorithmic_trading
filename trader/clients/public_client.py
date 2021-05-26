from trader.client import client
from pprint import pprint
from trader.global_utils import apply2all_methods, log
from binance.client import Client


@apply2all_methods(log)
class PublicClient:
    def __init__(self):
        self._client = client

    # def ping_server(self):
    #     res = self._client.ping()
    #     print(res)
    #     return res
    #
    # def get_server_time(self):
    #     time_res = self._client.get_server_time()
    #     pprint(time_res)
    #     return time_res
    #
    # def get_system_status(self):
    #     status = client.get_system_status()
    #     print(status)
    #     return status
    #
    # def get_exchange_info(self):
    #     info = self._client.get_exchange_info()
    #     pprint(info)
    #     f = open("result.txt", "w+")
    #     f.write(str(info))
    #     f.close()
    #     return info
    #
    # def get_symbol_info(self, symbol='BTCUSDT'):
    #     info = self._client.get_symbol_info(symbol)
    #     pprint(info)
    #     return info

    # def get_all_exchanges(self):
    #     exchanges = ccxt.exchanges
    #     pprint(exchanges)
    #     return exchanges
    #
    # def get_recent_trades(self, symbol='BTCUSDT'):
    #     trades = client.get_recent_trades(symbol=symbol)
    #     pprint(trades)
    #     return trades
    #
    # def get_symbol_avg_price(self, symbol='BTCUSDT'):
    #     avg_price = client.get_avg_price(symbol=symbol)
    #     pprint(avg_price)
    #     return avg_price
    #
    # def get24hr_ticker(self):
    #     tickers = client.get_ticker()
    #     pprint(tickers)
    #     return tickers
    #
    # def get_all_prices(self):
    #     info = client.get_all_tickers()
    #     pprint(info)
    #     return info
    #
    # def get_candles(self, symbol='BTCUSDT'):
    #     candles = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_30MINUTE)
    #     pprint(candles)
    #     return candles
