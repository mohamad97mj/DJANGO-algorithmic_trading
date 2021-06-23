import time
from trader.main.spot.models import SpotPosition, SpotBot


class SpotBotHandler:

    def __init__(self):
        self.bots: SpotBot = []

    def create_bot(self, exchange_id: str, credential_id: str, position: SpotPosition):
        new_bot = SpotBot(exchange_id=exchange_id, credential_id=credential_id, position=position)
        self.bots.append(new_bot)
        return new_bot

    def run_bots(self):
        while True:
            for bot in self.bots:
                print("in loop in run_bots")
                bot.run()
            time.sleep(1)
            print('in run_bots')
