import asyncio
from trader.bots import SpotBot
from trader.clients import PublicClient
from trader.exchange import ef, Exchange
from pprint import pprint


async def main():
    exchange = ef.create_exchange(exchange_id='binance')
    public_client = PublicClient(exchange=exchange)
    x = await public_client.fetch_ohlcv(timeframe='1m')
    pprint(x)
    await ef.close_all_exchages()
    # pprint(exchange.get_timeframes())

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
