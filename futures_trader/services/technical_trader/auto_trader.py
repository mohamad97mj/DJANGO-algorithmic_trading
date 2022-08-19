import queue
import time
from threading import Thread

from futures_trader.config import POSITION_MARGIN
from futures_trader.services.trader import FuturesBotTrader
from futures_trader.utils.app_vars import is_test
from futures_trader.clients.public_client import PublicClient
from spot_trader.services.ta import TechnicalAnalyser
from global_utils.my_logging import my_get_logger
from global_utils.catch_all_exceptions import catch_all_exceptions
from global_utils.retry_on_timeout import retry_on_timeout
from dataclasses import dataclass

signal_data_queue = queue.Queue()

rsi_muck_values = [22, 21, 20, 19, 18, 21, 22, 23, 24, 25, 26, 27, 28]
cci_muck_values = [
    (-120, 119), (-115, -110), (-100, -95), (-90, -60), (23, 24), (25, 26), (27, 28),
    (-120, -115), (-110, -100), (-95, -90), (-60, 23), (24, 25), (26, 27), (28, -120), (-115, -110), (-100, -95),
    (-90, -60), (23, 24), (25, 26), (27, 28), ]


@dataclass
class SymbolPositionConfig:
    trend: str = None
    tp_ratio: float = None
    leverage: int = None


symbols_position_config = {
    'LINK/USDT': SymbolPositionConfig(trend='up', leverage=10, tp_ratio=0.1),
    'UNI/USDT': SymbolPositionConfig(trend='up', leverage=10, tp_ratio=0.1),
    'ROSE/USDT': SymbolPositionConfig(trend='up', leverage=10, tp_ratio=0.1),
    'FTM/USDT': SymbolPositionConfig(trend='up', leverage=10, tp_ratio=0.1),
    'MATIC/USDT': SymbolPositionConfig(trend='up', leverage=10, tp_ratio=0.1),
    'MANA/USDT': SymbolPositionConfig(trend='up', leverage=10, tp_ratio=0.1),
    'TRX/USDT': SymbolPositionConfig(trend='up', leverage=10, tp_ratio=0.1),
    '1INCH/USDT': SymbolPositionConfig(trend='up', leverage=10, tp_ratio=0.1),
}


def alarm_position(symbol):
    timeframe = '1h'
    last_prev_cci = None
    while True:
        cci, prev_cci = TechnicalAnalyser.get_cci(symbol, timeframe, 40)
        if cci and prev_cci:
            if last_prev_cci != prev_cci:
                if prev_cci <= -100 <= cci:
                    send_telegram_message()
                elif last_prev_cci >= 100 >= cci:
                    send_telegram_message()
            last_prev_cci = prev_cci
        time.sleep(60)


def alarm_positions():
    symbols = PublicClient().load_markets()

    for symbol in symbols:
        t = Thread(target=alarm_position, args=(symbol,))
        t.start()


def send_telegram_message():
    pass


@catch_all_exceptions()
def start_technical_signal_generating_per_symbol(pb, symbol, timeframe, n):
    logger = my_get_logger()
    symbol_position_config = symbols_position_config[symbol]
    if False:
        cci, prev_cci = cci_muck_values.pop(0)
    else:
        cci, prev_cci = TechnicalAnalyser.get_cci(symbol, timeframe, n)
    macd, prev_macd = TechnicalAnalyser.get_macd(symbol)
    logger.info('{} {} {} {}'.format(symbol, cci, prev_cci, macd))
    last_prev_cci = None
    while True:
        is_signal = False
        if False:
            cci, prev_cci = cci_muck_values.pop(0)
        else:
            cci, prev_cci = TechnicalAnalyser.get_cci(symbol, timeframe, n)
        logger.info('{} {} {} {}'.format(symbol, cci, prev_cci, macd))
        if last_prev_cci != prev_cci:

            if symbol_position_config.trend in ('up', 'range'):
                if prev_cci <= -100 <= cci:
                    side = 'buy'
                    is_signal = True
                elif prev_cci <= -100 <= cci:
                    FuturesBotTrader.stop_bot(credential_id='kucoin_main', symbol=symbol)
            elif symbol_position_config.trend in ('down', 'range'):
                if prev_cci >= 100 >= cci:
                    side = 'sell'
                    is_signal = True
                elif prev_cci >= 100 >= cci:
                    FuturesBotTrader.stop_bot(credential_id='kucoin_main', symbol=symbol)

            if is_signal:
                price = pb.fetch_ticker(symbol=symbol)
                sign = 1 if side == 'buy' else -1
                tp_price = price * (1 + sign * symbol_position_config.tp_ratio)
                logger = my_get_logger()
                signal_data = {'symbol': symbol,
                               'leverage': symbol_position_config.leverage,
                               'steps': [{'entry_price': -1, }],
                               'targets': [{'tp_price: ': tp_price}],
                               'side': side}
                signal_data_queue.put(signal_data)
        last_prev_cci = prev_cci
        time.sleep(10)


def start_technical_signal_generating():
    timeframe = '1h'
    n = 20
    pb = PublicClient()
    # symbols = pb.load_markets()
    symbols = symbols_position_config.keys()

    for symbol in symbols:
        t = Thread(target=start_technical_signal_generating_per_symbol, args=(pb, symbol, timeframe, n,))
        t.start()


def consume_signal(signal_data):
    signal_data['setup_mode'] = 'auto'
    signal_data['source'] = 'technical'
    position_data = {
        'signal': signal_data,
        'margin': POSITION_MARGIN,
        'order_type': 'market'
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
    t1 = Thread(target=start_technical_signal_generating)
    t1.start()
    #
    t2 = Thread(target=start_signal_consuming)
    t2.start()
