from .my_websocket import MyConnectWebsocket
from kucoin.ws_client import KucoinWsClient


class MyKucoinWsClient(KucoinWsClient):

    @classmethod
    async def create(cls, loop, client, callback, private=False):
        self = MyKucoinWsClient()
        self._loop = loop
        self._client = client
        self._private = private
        self._callback = callback
        self._conn = MyConnectWebsocket(loop, self._client, self._recv, private)
        return self

    def close_connection(self):
        self._conn.close_socket()
