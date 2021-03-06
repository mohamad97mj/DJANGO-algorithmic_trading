import asyncio
from kucoin.websocket.websocket import ConnectWebsocket


class MyConnectWebsocket(ConnectWebsocket):

    async def _close(self):
        await self._socket.close()

    def close_socket(self):
        asyncio.ensure_future(self._close(), loop=self._loop)
