from .bot_handler import SpotBotHandler
from .models import SpotPosition


class SpotTrader:
    def __init__(self):
        self._bot_handler = SpotBotHandler()

    def open_position(self, exchange_id: str, credential_id: str, position: SpotPosition):
        self._bot_handler.create_bot(exchange_id=exchange_id, credential_id=credential_id, position=position)


trader = SpotTrader()
