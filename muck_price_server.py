import asyncio
import websockets
from websockets.exceptions import ConnectionClosedError
import time

prices = {
    'TRX/USDT': [
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.96,
        0.98,
        0.98,
        0.98,
        0.98,
        0.98,
        0.98,
        0.98,
        0.98,
        0.98,
        0.98,
        0.98,
        0.99,
        0.99,
        0.99,
        0.99,
        0.99,
        0.99,
        0.99,
        0.99,
        0.99,
        0.99,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1.02,
        1.02,
        1.02,
        1.02,
        1.02,
        1.02,
        1.02,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.05,
        1.08,
        1.08,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
        1.11,
    ]
}


async def send_price(websocket):
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
