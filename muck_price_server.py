import asyncio
import websockets
from websockets.exceptions import ConnectionClosedError
import time

prices = {
    'BTC/USDT': [
        37000,
        37000,
        37000,
        37000,
        37000,
        36000,
        35000,
        34000,
        33500,
        33000,
        33000,
        32500,
        32000,
        32000,
        32000,
        34000,
        35000,
        36000,
        38000,
        40000,
        42000,
        43000,
        43000,
        43000,
        43000,
        44000,
        44000,
        44000,
        44000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        45000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
        48000,
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
                time.sleep(2)
            except ConnectionClosedError as e:
                print('reconnecting')
                break


start_server = websockets.serve(send_price, "localhost", 9001)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
