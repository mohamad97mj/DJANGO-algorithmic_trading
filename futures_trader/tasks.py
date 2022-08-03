import gc
from celery import shared_task
from spot_trader.services.ta import TechnicalAnalyser
from fetch import symbols
from futures_trader.services.external_signal_trader.auto_trader import create_client
from spot_trader.clients import PublicClient
from futures_trader.services.trader import FuturesBotTrader
from global_utils.my_logging import my_get_logger
from time import sleep

myclient = create_client()


def notify_in_telegram(message):
    myclient.get_dialogs()
    entity = myclient.get_entity('My alarms')
    myclient.send_message(entity, message)


@shared_task
def technical_auto_trade():
    global myclient
    if not myclient:
        myclient = create_client()
    appropriate_longs = []
    appropriate_shorts = []
    for symbol in symbols:

        logger = my_get_logger()
        cci, prev_cci = TechnicalAnalyser.get_cci(symbol=symbol,
                                                  timeframe='1h',
                                                  n=20)
        macd, prev_macd = TechnicalAnalyser.get_macd(symbol)
        bbd, bbu = TechnicalAnalyser.get_bollinger_band(symbol, timeframe='1h', n=20)
        logger.info("""
            symbol: {},
            prev_cci: {},
            cci: {},
            prev_macd: {},
            macd: {},
            bbd: {},
            bbu: {}
        """.format(symbol, prev_cci, cci, prev_macd, macd, bbd, bbu))
        is_appropriate = False
        risk = side = sign = None
        pbc = PublicClient()
        ohlc = pbc.fetch_ohlcv(symbol, timeframe='1h', limit=1)[0]
        close = ohlc[4]

        if prev_cci < -100 < cci and macd > 0 and prev_macd > 0:
            side = 'buy'
            sign = 1
            risk = (close - bbd) / close
            reward = (bbu - close) / close
            rr = risk / reward
            logger.info('rr: {}'.format(rr))
            if 0 < rr < 1 / 3:
                is_appropriate = True
                appropriate_longs.append(symbol)
        elif prev_cci > 100 > cci and macd < 0 and prev_macd < 0:
            side = 'sell'
            sign = -1
            risk = (bbu - close) / close
            reward = (close - bbd) / close
            rr = risk / reward
            logger.info('rr: {}'.format(rr))
            if 0 < rr < 1 / 3:
                is_appropriate = True
                appropriate_shorts.append(symbol)
        if is_appropriate:
            logger.info("""
            position is appropriate
            """)
            tp1 = close * (1 + sign * risk)
            tp2 = close * (1 + sign * 2 * risk)
            stoploss = close * (1 - sign * risk)
            leverage = min(30 / (100 * risk), 20)
            signal_data = {'symbol': symbol,
                           'leverage': leverage,
                           'steps': [{'entry_price': -1, }],
                           'targets': [{'tp_price': tp1}, {'tp_price': tp2}],
                           'side': side,
                           'stoploss': {'trigger_price': stoploss}}
            position_data = {
                'signal': signal_data,
                'margin': 2,
                'order_type': 'market'
            }
            credential_id = 'kucoin_main'
            bot_data = {
                'exchange_id': 'kucoin',
                'credential_id': credential_id,
                'strategy': 'manual',
                'position': position_data,
            }
            FuturesBotTrader.create_bot(bot_data)
        sleep(1)

    message = 'appropriate symbols for long positions:{}\n appropriate symbols for short positions:{}'.format(
        appropriate_longs, appropriate_shorts)
    notify_in_telegram(message)
    gc.collect()
