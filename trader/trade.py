import asyncio
from trader.main.spot.trader import trader
from threading import Thread


async def trade():

    t1 = Thread(target=trader.start)
    t1.start()
