import time
from typing import List
from trader.main.spot.models import SpotPosition, SpotBot


class SpotBotHandler:

    def __init__(self):
        self._bots: List[SpotBot] = []
        self._prices: dict = {}

    def create_bot(self, exchange_id: str, credential_id: str, strategy: str, position: SpotPosition):
        new_bot = SpotBot(exchange_id=exchange_id, credential_id=credential_id, strategy=strategy, position=position)
        self._bots.append(new_bot)
        new_bot.save()
        return new_bot

    def reload_bots(self):
        self._bots = list(SpotBot.objects.all())
        for bot in self._bots:
            bot.reload()

    def _is_prices_available(self, symbols: List):
        is_available = True
        for symbol in symbols:
            if not (symbol in self._prices and self._prices[symbol]):
                is_available = False

        return is_available

    def run_bots(self):
        # cancel previous orders
        while True:
            for bot in self._bots:
                price_required_symbols = bot.get_price_required_symbols()
                if self._is_prices_available(price_required_symbols):
                    bot.run(self._prices)

            time.sleep(1)
