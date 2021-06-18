from .spot_bot_handler import SpotBotHandler


class Trader:
    def __init__(self):
        self._spot_bot_handler = SpotBotHandler()
        # self._future_bot_handler = FutureBotHandler()

    def open_position(self):
        pass
