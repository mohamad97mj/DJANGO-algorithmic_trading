from trader.models import Operation
from trader.exchange import ef
from trader.bots.spot.models import SpotBot
from binance import ThreadedWebsocketManager


class BotGroupHandler:

    def __init__(self, symbol):
        self.symbol = symbol
        self.bots = []

    def create_bot(self, exchange_id, credential_id, position):
        new_bot = SpotBot.objects.create(exchange_id=exchange_id, credential_id=credential_id, position=position)
        self.bots.append(new_bot)

    def run_bots(self):
        pass
