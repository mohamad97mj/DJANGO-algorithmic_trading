import asyncio
from .bot_handler import SpotBotHandler
from .models import SpotPosition


class SpotTrader:
    def __init__(self):
        self._bot_handler = SpotBotHandler()

    def create_bot(self, exchange_id: str, credential_id: str, strategy: str, position_data: dict):
        return self._bot_handler.create_bot(exchange_id=exchange_id,
                                            credential_id=credential_id,
                                            strategy=strategy,
                                            position_data=position_data)

    def edit_position(self, bot_id, new_position_data):
        return self._bot_handler.edit_position(
            bot_id,
            new_position_data)

    def get_bot(self, bot_id):
        return self._bot_handler.get_bot(bot_id=bot_id)

    def start(self):
        self._bot_handler.reload_bots()
        self._bot_handler.run_bots()


trader = SpotTrader()
