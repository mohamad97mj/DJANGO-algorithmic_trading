import asyncio
import websockets
from websockets.exceptions import ConnectionClosedError
import time

prices = {
    'DOT/USDT': [
        30,
        30,
        29,
        29,
        28,
        28,
        31,
        31,
        32,
        32,
        33,
        33,
        34,
        35,
        36,
        37,
        38,
        38,
        39,
        39,
        40,
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
