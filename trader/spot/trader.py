from trader.spot.bot_handler import SpotBotHandler
from trader.models import SpotPosition


class SpotTrader:
    def __init__(self):
        self._bot_handler = SpotBotHandler()

    def open_position(self, credential_id: str, position: SpotTrader):
        pass


trader = SpotTrader()
