from threading import Thread
from futures_trader.services import FuturesBotTrader, start_auto_trading
from .utils.app_vars import enable_auto_external_signal_trading


def trade():
    t1 = Thread(target=FuturesBotTrader.start_trading)
    t1.start()

    if enable_auto_external_signal_trading:
        t2 = Thread(target=start_auto_trading)
        t2.start()
