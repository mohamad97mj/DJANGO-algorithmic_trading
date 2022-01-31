from threading import Thread
from spot_trader.services import SpotBotTrader


def trade():
    t1 = Thread(target=SpotBotTrader.start_trading)
    t1.start()


