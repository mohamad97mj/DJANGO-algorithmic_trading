import time
from pprint import pprint
from typing import List
from global_utils import retry_on_timeout, async_retry_on_timeout, my_get_logger
from trader.main.spot.models import SpotPosition, SpotBot
from trader.clients import PublicClient, PrivateClient
from trader.utils import with2without_slash, CacheUtils
import asyncio
from binance import AsyncClient, BinanceSocketManager
from threading import Thread
from aiohttp.client_exceptions import ClientConnectorError
from dataclasses import dataclass
from concurrent.futures._base import TimeoutError


@dataclass()
class PriceTicker:
    thread: Thread
    client: AsyncClient = None


class SpotBotHandler:

    def __init__(self):
        self._bots: List[SpotBot] = []
        self._public_clients = {}
        self._price_tickers = {}

    def create_bot(self, exchange_id: str, credential_id: str, strategy: str, position: SpotPosition):
        new_bot = SpotBot(exchange_id=exchange_id, credential_id=credential_id, strategy=strategy, position=position)
        self.init_bot_requirements(bot=new_bot)
        self._bots.append(new_bot)
        new_bot.save()
        return new_bot

    def reload_bots(self):
        self._bots = list(SpotBot.objects.all())
        for bot in self._bots:
            self.init_bot_requirements(bot)
            bot.reload()

    def init_bot_requirements(self, bot):
        private_client = PrivateClient(exchange_id=bot.exchange_id, credential_id=bot.credential_id)
        if bot.exchange_id in self._public_clients:
            public_client = self._public_clients[bot.exchange_id]
        else:
            public_client = PublicClient(exchange_id=bot.exchange_id)
            self._public_clients[bot.exchange_id] = public_client
        bot.init_requirements(private_client=private_client, public_client=public_client)

    def run_bots(self):
        # start = int(time.time())
        while True:
            for bot in self._bots:

                # finish = int(time.time())
                # if finish - start > 10:
                #     bot.reset_strategy()
                #
                # print(finish - start)

                price_required_symbols = bot.get_price_required_symbols()
                symbol_prices = self._get_prices_if_available(bot.exchange_id, price_required_symbols)
                while not symbol_prices:
                    self._start_symbols_price_ticker(bot.exchange_id, price_required_symbols)
                    time.sleep(7)
                    symbol_prices = self._get_prices_if_available(bot.exchange_id, price_required_symbols)

                logger = my_get_logger()
                logger.info('symbol_prices: {}'.format(symbol_prices))
                bot.run(symbol_prices)

            time.sleep(2)

    def _get_prices_if_available(self, exchange_id, symbols: List):
        symbol_prices = self._read_prices(exchange_id, symbols)
        for symbol in symbols:
            if not (symbol in symbol_prices and symbol_prices[symbol]):
                return

        return symbol_prices

    def _start_symbols_price_ticker(self, exchange_id, symbols: List):

        symbol_prices = self._read_prices(exchange_id, symbols)

        for symbol in symbols:
            if not (symbol in symbol_prices and symbol_prices[symbol]):
                if symbol not in self._price_tickers or self._price_tickers[symbol].client:
                    if symbol in self._price_tickers:
                        asyncio.run(self._price_tickers[symbol].client.close_connection())

                    self._init_price_ticker(exchange_id, symbol)

    def _init_price_ticker(self, exchange_id, symbol):
        t = Thread(target=asyncio.run, args=(self._start_symbol_price_ticker(exchange_id, symbol),))
        self._price_tickers[symbol] = PriceTicker(t)
        t.start()

    async def _start_symbol_price_ticker(self, exchange_id, symbol):
        client = await async_retry_on_timeout(
            self._public_clients[exchange_id],
            timeout_errors=(ClientConnectorError, TimeoutError))(self._get_async_client)()
        self._price_tickers[symbol].client = client

        bm = BinanceSocketManager(client)
        ts = bm.symbol_ticker_socket(with2without_slash(symbol))

        cache_name = '{}_price'.format(exchange_id)

        async with ts as tscm:
            while True:
                try:
                    res = await tscm.recv()
                    if res['e'] != 'error':
                        CacheUtils.write_to_cache(symbol, float(res['c']), cache_name)
                except Exception as e:
                    print(e)

    async def _get_async_client(self):
        return await AsyncClient.create()

    def _read_prices(self, exchange_id, symbols):
        cache_name = '{}_price'.format(exchange_id)
        return {
            symbol: CacheUtils.read_from_cache(symbol, cache_name) for symbol in symbols
        }
