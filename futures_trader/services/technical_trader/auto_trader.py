import queue
import time
from threading import Thread

from futures_trader.config import position_margin
from futures_trader.services.trader import FuturesBotTrader
from futures_trader.utils.app_vars import is_test
from futures_trader.clients.public_client import PublicClient
from spot_trader.services.ta import TechnicalAnalyser
from global_utils.my_logging import my_get_logger

signal_data_queue = queue.Queue()

rsi_muck_values = [22, 21, 20, 19, 18, 21, 22, 23, 24, 25, 26, 27, 28]


def start_signal_generating():
    condition_is_normal = True
    logger = my_get_logger()
    pb = PublicClient()
    symbol = 'BTC/USDT'
    tp_ratio = 0.011
    sl_ratio = 0.009
    timeframe = '5m'

    while True:
        if True:
            rsi = rsi_muck_values.pop(0)
        else:
            rsi = TechnicalAnalyser.get_rsi(symbol=symbol, timeframe=timeframe)

        price = pb.fetch_ticker(symbol=symbol)
        logger.debug('rsi: {}, price: {}, condition_is_normal: {}'.format(rsi, price, condition_is_normal))
        if rsi <= 20 or rsi >= 80:
            signal_data = {'symbol': symbol, 'steps': [{'entry_price': price, }, ]}
            if rsi <= 20:
                signal_data['side'] = 'buy'
                signal_data['targets'] = [{'tp_price': int(price * (1 + tp_ratio)), }, ]
                signal_data['stoploss'] = {'trigger_price': int(price * (1 - sl_ratio))}
            else:
                signal_data['side'] = 'sell'
                signal_data['targets'] = [{'tp_price': int(price * (1 - tp_ratio)), }, ]
                signal_data['stoploss'] = {'trigger_price': int(price * (1 + sl_ratio))}
            if condition_is_normal:
                logger.info('new signal data was generated')
                signal_data_queue.put(signal_data)
                condition_is_normal = False
        elif 35 < rsi < 65:
            condition_is_normal = True
        time.sleep(10)


def consume_signal(signal_data):
    signal_data['setup_mode'] = 'auto'
    signal_data['leverage'] = 50
    signal_data['source'] = 'technical'
    position_data = {
        'signal': signal_data,
        'margin': position_margin,
        'order_type': 'limit'
    }
    credential_id = 'kucoin_main'
    bot_data = {
        'exchange_id': 'kucoin',
        'credential_id': credential_id,
        'strategy': 'manual',
        'position': position_data,
    }
    logger = my_get_logger()
    logger.info('new signal data was consumed')
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
