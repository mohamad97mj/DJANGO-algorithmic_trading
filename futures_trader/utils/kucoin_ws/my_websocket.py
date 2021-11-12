import asyncio
from kucoin_futures.websocket.websocket import ConnectWebsocket


class MyConnectWebsocket(ConnectWebsocket):

    async def _close(self):
        if self._socket:
            await self._socket.close()

    def close_socket(self):
        asyncio.ensure_future(self._close(), loop=self._loop)
