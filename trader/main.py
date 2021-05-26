import asyncio
from trader.bots import SpotTrader
from trader.clients import PublicClient
from trader.exchange import ExchageFactory, Exchange


async def main():
    ef = ExchageFactory()

    # public_client = PublicClient()
    # print('exchanges are:', public_client.get_exchanges())
    exchange = ef.create_exchange(exchange_id='binance')
    public_client = PublicClient(exchange=exchange)
    markets = await public_client.get_markets()
    print(markets)

    await ef.close_all_exchages()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
