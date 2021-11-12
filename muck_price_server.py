import asyncio
import websockets
from websockets.exceptions import ConnectionClosedError
import time

prices = {
    'TRX/USDT': [
        0.105,
        0.105,
        0.106,
        0.107,
        0.103,
        0.103,
        0.103,
        0.101,
        0.101,
        0.101,
        0.101,
        0.101,
        0.101,
        0.101,
        0.101,
        0.101,
        0.108,
        0.110,
        0.112,
        0.112,
        0.113,
        0.113,
        0.113,
        0.115,
        0.120,
        0.120,
        0.120,
        0.120,
        0.118,
        0.118,
        0.118,
        0.118,
        0.115,
        0.115,
        0.115,
        0.115,
        0.110,
        0.110,
        0.100,
        0.100,
        0.100,
    ]
}


async def send_price(websocket, path):
    while True:
        symbol = await websocket.recv()
        print(symbol)
        while True:
            try:
                price = prices[symbol].pop(0)
                await websocket.send(str(price))
                time.sleep(1)
            except ConnectionClosedError as e:
                print('reconnecting')
                break


start_server = websockets.serve(send_price, "localhost", 9000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
