import asyncio
from .bot_handler import SpotBotHandler
from .models import SpotPosition


class SpotTrader:
    def __init__(self):
        self._bot_handler = SpotBotHandler()

    def open_position(self, exchange_id: str, credential_id: str, strategy: str, position: SpotPosition):
        return self._bot_handler.create_bot(exchange_id=exchange_id,
                                            credential_id=credential_id,
                                            strategy=strategy,
                                            position=position)

    def start(self):
        self._bot_handler.reload_bots()
        self._bot_handler.run_bots()


trader = SpotTrader()
