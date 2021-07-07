import time
from typing import List
from trader.main.spot.models import SpotPosition, SpotBot
from binance import ThreadedWebsocketManager
from trader.clients import PublicClient, PrivateClient


class SpotBotHandler:

    def __init__(self):
        self._bots: List[SpotBot] = []
        self._symbol_prices: dict = {}
        self._public_clients = {}

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
        # cancel previous orders
        while True:
            for bot in self._bots:
                price_required_symbols = bot.get_price_required_symbols()

                while not self._is_prices_available(bot.exchange_id, price_required_symbols):
                    time.sleep(1)
                bot.run(self._symbol_prices)
            time.sleep(1)

    def _is_prices_available(self, exchange_id, symbols: List):
        is_available = True
        for symbol in symbols:
            if not (symbol in self._symbol_prices and
                    exchange_id in self._symbol_prices[symbol] and
                    self._symbol_prices[symbol][exchange_id]):
                is_available = False

        return is_available

    def _start_price_ticker(self, symbols: List):

        twm = ThreadedWebsocketManager()
        twm.start()
        for symbol in symbols:
            if symbol not in self._symbol_prices:
                twm.start_symbol_ticker_socket(callback=self._handle_price_ticker_socket_message, symbol=symbol)

    def _handle_price_ticker_socket_message(self, msg):
        # print(f"message type: {msg['e']}")
        print(msg)
