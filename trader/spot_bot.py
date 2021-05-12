from .client import client
from pprint import pprint


class SpotBotClient:
    def __init__(self):
        self._client = client

    def get_exchange_info(self):
        res = client.get_exchange_info()
        pprint(res)
        return res


