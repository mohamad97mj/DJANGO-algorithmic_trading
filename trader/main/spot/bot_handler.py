import time
from .models import SpotPosition, SpotBot


class SpotBotHandler:

    def __init__(self):
        self.bots: SpotBot = []

    def create_bot(self, exchange_id, credential_id, position: SpotPosition):
        new_bot = SpotBot.objects.create()
        self.bots.append(new_bot)

    def run_bots(self):
        while True:
            for bot in self.bots:
                bot.run()
            time.sleep(5)