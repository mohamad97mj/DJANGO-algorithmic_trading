import time
from typing import List
from trader.main.spot.models import SpotPosition, SpotBot


class SpotBotHandler:

    def __init__(self):
        self.bots: List[SpotBot] = []

    def create_bot(self, exchange_id: str, credential_id: str, strategy: str, position: SpotPosition):
        new_bot = SpotBot(exchange_id=exchange_id, credential_id=credential_id, strategy=strategy, position=position)
        self.bots.append(new_bot)
        new_bot.save()
        return new_bot

    def reload_bots(self):
        self.bots = list(SpotBot.objects.all())
        for bot in self.bots:
            bot.reload()

    def run_bots(self):
        # cancel previous orders
        while True:
            for bot in self.bots:
                print("in loop in run_bots")
                bot.run()
            time.sleep(1)
            print('in run_bots')
