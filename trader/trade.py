from threading import Thread
from trader.main.spot.services import SpotBotTrader


def trade():
    t1 = Thread(target=SpotBotTrader.start_trading)
    t1.start()
