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

