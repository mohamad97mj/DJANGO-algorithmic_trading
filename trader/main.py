import asyncio
from trader.bots import SpotTrader
from trader.clients import PublicClient
from trader.exchange import ExchageFactory, Exchange
from pprint import pprint


async def main():
    ef = ExchageFactory()
    exchange = ef.create_exchange(exchange_id='binance')
    public_client = PublicClient(exchange=exchange)
    pprint(await public_client.fetch_tickers())
    await ef.close_all_exchages()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
