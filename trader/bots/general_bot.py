from trader.client import client
from pprint import pprint


class GeneralBot:
    def __init__(self):
        self._client = client

    def ping_server(self):
        self._client.ping()
