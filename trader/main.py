import asyncio
from trader.bots import SpotBot
from trader.clients import PublicClient, PrivateClient
from trader.exchange import ef, Exchange
from pprint import pprint


async def main():
    public_client = PublicClient(exchange_id='binance')
    private_client = PrivateClient(credential_id='Main')

    await ef.close_all_exchages()
    # pprint(exchange.get_timeframes())


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
