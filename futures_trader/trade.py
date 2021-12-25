from threading import Thread
from futures_trader.services import FuturesBotTrader
from futures_trader.services import start_signal_receiving, start_signal_consuming


def trade():
    t1 = Thread(target=FuturesBotTrader.start_trading)
    t1.start()

    t2 = Thread(target=start_signal_receiving)
    t2.start()

    t3 = Thread(target=start_signal_consuming)
    t3.start()
