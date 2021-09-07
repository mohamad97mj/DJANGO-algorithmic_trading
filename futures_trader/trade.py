from threading import Thread
from futures_trader.services import FuturesBotTrader


def trade():
    t1 = Thread(target=FuturesBotTrader.start_trading)
    t1.start()
