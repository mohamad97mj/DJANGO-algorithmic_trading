import queue
import time
from threading import Thread

from futures_trader.config import position_margin
from futures_trader.services.trader import FuturesBotTrader
from futures_trader.clients.public_client import PublicClient
from spot_trader.services.ta import TechnicalAnalyser
from global_utils.my_logging import my_get_logger

signal_data_queue = queue.Queue()


class muck_position:
    pass


def start_signal_generating():
    logger = my_get_logger()
    pb = PublicClient()

    while True:
        rsi = TechnicalAnalyser.get_rsi(symbol='BTC/USDT', timeframe='5m')
        price = pb.fetch_ticker(symbol='BTC/USDT')
        logger.info('rsi: {}, price: {}'.format(rsi, price))
        time.sleep(60)


def consume_signal(signal_data):
    signal_data['setup_mode'] = 'auto'
    signal_data['leverage'] = 25
    position_data = {
        'signal': signal_data,
    }
    credential_id = 'kucoin_main'
    if signal_data['type'] in ('single', 'primary'):
        position_data['margin'] = position_margin
        bot_data = {
            'exchange_id': 'kucoin',
            'credential_id': credential_id,
            'strategy': 'manual',
            'position': position_data,
        }
        FuturesBotTrader.create_bot(bot_data)


def start_signal_consuming():
    while True:
        if not signal_data_queue.empty():
            signal_data = signal_data_queue.get()
            consume_signal(signal_data)

        time.sleep(1)


def start_auto_trading():
    t1 = Thread(target=start_signal_generating)
    t1.start()

    t2 = Thread(target=start_signal_consuming)
    t2.start()
