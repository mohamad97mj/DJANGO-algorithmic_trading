from trader.client import client
from pprint import pprint
from trader.global_utils import apply2all_methods, log


@apply2all_methods(log)
class GeneralBot:
    def __init__(self):
        self._client = client

    def ping_server(self):
        res = self._client.ping()
        print(res)
        return res

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
        f = open("result.txt", "w+")
        f.write(str(info))
        f.close()
        return info

    def get_symbol_info(self, symbol='BTCUSDT'):
        info = self._client.get_symbol_info(symbol)
        pprint(info)
        return info


