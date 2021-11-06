import asyncio
from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient


async def main():
    async def deal_msg(msg):
        if msg['topic'] == '/contractMarket/level2:XBTUSDM':
            print(f'Get XBTUSDM Ticker:{msg["data"]}')
        elif msg['topic'] == '/contractMarket/level3:XBTUSDTM':
            print(f'Get XBTUSDTM level3:{msg["data"]}')

    # is public
    # client = WsToken()
    # is private
    client = WsToken(key='', secret='', passphrase='', is_sandbox=False, url='')
    # is sandbox
    # client = WsToken(is_sandbox=True)
    ws_client = await KucoinFuturesWsClient.create(loop, client, deal_msg, private=False)
    await ws_client.subscribe('/contractMarket/level2:XBTUSDM')
    await ws_client.subscribe('/contractMarket/level3:XBTUSDM')
    while True:
        await asyncio.sleep(10, loop=loop)
        await ws_client.unsubscribe('/contractMarket/level2:XBTUSDM')
        await ws_client.unsubscribe('/contractMarket/level3:XBTUSDM')



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
