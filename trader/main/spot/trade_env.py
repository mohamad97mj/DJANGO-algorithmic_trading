import asyncio
from .trader import trader


async def trade():
    trader.start()


asyncio.get_event_loop().run_until_complete(trade())
