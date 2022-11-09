from threading import Thread
from futures_trader.services import FuturesBotTrader
from .utils.app_vars import enable_external_signal_auto_trading, enable_technical_auto_trading


def trade():
    t1 = Thread(target=FuturesBotTrader.start_trading)
    t1.start()

    from futures_trader.services.external_signal_trader import auto_trader

    # if enable_external_signal_auto_trading:
    #     from futures_trader.services.external_signal_trader import start_auto_trading
    #     t2 = Thread(target=start_auto_trading)
    #     t2.start()

    # if enable_technical_auto_trading:
    #     from futures_trader.services.technical_trader.auto_trader import start_auto_trading
    #     t3 = Thread(target=start_auto_trading)
    #     t3.start()

