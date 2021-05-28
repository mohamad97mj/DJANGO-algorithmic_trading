import asyncio
from trader.bots import SpotBot
from trader.clients import PublicClient, PrivateClient
from trader.exchange import ef, Exchange
from pprint import pprint


async def main():
    # public_client = PublicClient(exchange_id='binance')
    private_client = PrivateClient(exchange_id='binance', credential_id='test')
    await private_client.create_market_buy_order('BNB/USDT', 10)
    pprint(await private_client.fetch_total_balance())
    # pprint(await private_client.fetch_open_orders('BTC/USDT'))
    pprint(await private_client.fetch_my_trades('BNB/USDT'))
    await ef.close_all_exchages()
    # pprint(exchange.get_timeframes())
