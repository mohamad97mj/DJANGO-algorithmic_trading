from trader.client import client
from pprint import pprint


class GeneralBot:
    def __init__(self):
        self._client = client

    def ping_server(self):
        self._client.ping()

    def get_server_time(self):
        time_res = self._client.get_server_time()
        pprint(time_res)
        return time_res

    def get_system_status(self):
        status = client.get_system_status()
        print(status)
        return status

    def get_exchange_info(self):
        info = self._client.get_exchange_info()
        pprint(info)
        return info

    def get_symbol_info(self, symbol='BTCUSDT'):
        info = self._client.get_symbol_info(symbol)
        pprint(info)
        return info

    def get_all_coins_info(self):
        info = client.get_all_tickers()
        pprint(info)
        return info


