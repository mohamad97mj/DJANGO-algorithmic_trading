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

    def edit_none_triggered_steps(self, bot_id, *args, **kwargs):
        return self._bot_handler.run_strategy_developer_command(
            bot_id,
            'edit_none_triggered_steps',
            *args,
            **kwargs)


    def start(self):
        self._bot_handler.reload_bots()
        self._bot_handler.run_bots()


trader = SpotTrader()
