import yfinance as yf
import gc
import pandas
import numpy
import talib
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates

from celery import shared_task
from collections import OrderedDict
from datetime import datetime, timedelta
from mplfinance.original_flavor import candlestick_ohlc
from ta.trend import MACD
from candlestick import has_long_candlestick_confirmation, has_short_candlestick_confirmation
from futures_trader.services.external_signal_trader.auto_trader import create_client
from futures_trader.models import FuturesSignal
from global_utils.my_logging import my_get_logger
from global_utils.catch_all_exceptions import catch_all_exceptions

myclient = create_client()

PATTERNS = {
    'CDL2CROWS': 1,  # Two Crows,
    'CDL3BLACKCROWS': 3,  # Three Black Crows,
    'CDL3INSIDE': 2,  # Three Inside Up/Down,
    'CDL3OUTSIDE': 2,  # Three Outside Up/Down,
    'CDL3STARSINSOUTH': 3,  # Three Stars In The South,
    'CDL3WHITESOLDIERS': 3,  # Three Advancing White Soldiers,
    'CDLABANDONEDBABY': 3,  # Abandoned Baby,
    'CDLADVANCEBLOCK': 2,  # Advance Block,
    'CDLBELTHOLD': 1,  # Belt-hold,
    'CDLBREAKAWAY': 1,  # Breakaway,
    'CDLCLOSINGMARUBOZU': 1,  # Closing Marubozu,
    'CDLCONCEALBABYSWALL': 3,  # Concealing Baby Swallow,
    'CDLCOUNTERATTACK': 1,  # Counterattack,
    'CDLDARKCLOUDCOVER': 2,  # Dark Cloud Cover,
    'CDLDOJI': '1',  # Doji,
    'CDLDOJISTAR': 2,  # Doji Star,
    'CDLDRAGONFLYDOJI': 2,  # Dragonfly Doji,
    'CDLENGULFING': 2,  # Engulfing Pattern,
    'CDLEVENINGDOJISTAR': 3,  # Evening Doji Star,
    'CDLEVENINGSTAR': 3,  # Evening Star,
    'CDLGAPSIDESIDEWHITE': 1,  # Up/Down-gap side-by-side white lines,
    'CDLGRAVESTONEDOJI': 2,  # Gravestone Doji,
    'CDLHAMMER': 1,  # Hammer,
    'CDLHANGINGMAN': 1,  # Hanging Man,
    'CDLHARAMI': 1,  # Harami Pattern,
    'CDLHARAMICROSS': 1,  # Harami Cross Pattern,
    'CDLHIGHWAVE': 1,  # High-Wave Candle,
    'CDLHOMINGPIGEON': 2,  # Homing Pigeon,
    'CDLIDENTICAL3CROWS': 3,  # Identical Three Crows,
    'CDLINNECK': 1,  # In-Neck Pattern,
    'CDLINVERTEDHAMMER': 1,  # Inverted Hammer,
    'CDLKICKING': 2,  # Kicking,
    'CDLKICKINGBYLENGTH': 2,  # Kicking - bull/bear determined by the longer marubozu,
    'CDLLADDERBOTTOM': 1,  # Ladder Bottom,
    'CDLLONGLEGGEDDOJI': 1,  # Long Legged Doji,
    'CDLLONGLINE': 1,  # Long Line Candle,
    'CDLMARUBOZU': 1,  # Marubozu,
    'CDLMATCHINGLOW': 1,  # Matching Low,
    'CDLMATHOLD': 1,  # Mat Hold,
    'CDLMORNINGDOJISTAR': 3,  # Morning Doji Star,
    'CDLMORNINGSTAR': 3,  # Morning Star,
    'CDLONNECK': 1,  # On-Neck Pattern,
    'CDLPIERCING': 1,  # Piercing Pattern,
    'CDLRICKSHAWMAN': 1,  # Rickshaw Man,
    'CDLRISEFALL3METHODS': 2,  # Rising/Falling Three Methods,
    'CDLSEPARATINGLINES': 2,  # Separating Lines,
    'CDLSHOOTINGSTAR': 1,  # Shooting Star,
    'CDLSHORTLINE': 1,  # Short Line Candle,
    'CDLSPINNINGTOP': 1,  # Spinning Top,
    'CDLSTALLEDPATTERN': 2,  # Stalled Pattern,
    'CDLSTICKSANDWICH': 1,  # Stick Sandwich,
    'CDLTAKURI': 2,  # Takuri (Dragonfly Doji with very long lower shadow),
    'CDLTASUKIGAP': 1,  # Tasuki Gap,
    'CDLTHRUSTING': 1,  # Thrusting Pattern,
    'CDLTRISTAR': 2,  # Tristar Pattern,
    'CDLUNIQUE3RIVER': '2',  # Unique 3 River,
    'CDLUPSIDEGAP2CROWS': 1,  # Upside Gap Two Crows,
    'CDLXSIDEGAP3METHODS': 2,
}

symbols = [
    'AUDCAD=X',
    'AUDCHF=X',
    'AUDEUR=X',
    'AUDGBP=X',
    'AUDJPY=X',
    'AUDNZD=X',
    'AUDUSD=X',
    'CADAUD=X',
    'CADCHF=X',
    'CADEUR=X',
    'CADGBP=X',
    'CADJPY=X',
    'CADNZD=X',
    'CHFAUD=X',
    'CHFCAD=X',
    'CHFEUR=X',
    'CHFEUR=X',
    'CHFGBP=X',
    'CHFJPY=X',
    'CHFNZD=X',
    'EURAUD=X',
    'EURCAD=X',
    'EURCHF=X',
    'EURGBP=X',
    'EURJPY=X',
    'EURNZD=X',
    'EURUSD=X',
    'GBPAUD=X',
    'GBPCAD=X',
    'GBPCHF=X',
    'GBPEUR=X',
    'GBPJPY=X',
    'GBPNZD=X',
    'JPYAUD=X',
    'JPYCAD=X',
    'JPYCHF=X',
    'JPYEUR=X',
    'JPYGBP=X',
    'JPYNZD=X',
    'NZDAUD=X',
    'NZDCAD=X',
    'NZDCHF=X',
    'NZDEUR=X',
    'NZDGBP=X',
    'NZDUSD=X',
    'CAD=X',
    'CHF=X',
    'JPY=X',
]


def get_ccis(ohlcs, n=20):
    np_array = numpy.array(ohlcs)
    high_prices = pandas.Series(np_array[:, 1])
    low_prices = pandas.Series(np_array[:, 2])
    close_prices = pandas.Series(np_array[:, 3])

    TP = (high_prices + low_prices + close_prices) / 3
    sma = TP.rolling(n).mean()
    mad = TP.rolling(n).apply(lambda x: pandas.Series(x).mad())
    CCI = (TP - sma) / (0.015 * mad)
    CCI_list = CCI.to_list()

    return CCI_list


def get_macds(ohlcs):
    np_array = numpy.array(ohlcs)
    close_prices = pandas.Series(np_array[:, 3])
    macd = MACD(close=close_prices)
    return macd.macd_diff().tolist()


def get_sma(ohlcs, n):
    np_array = numpy.array(ohlcs)
    close_prices = pandas.Series(np_array[:, 3])
    return close_prices.rolling(n).mean()


def get_bollinger_bands(ohlcs, n=20):
    np_array = numpy.array(ohlcs)
    sma = get_sma(ohlcs, n)
    close_prices = pandas.Series(np_array[:, 3])
    std = close_prices.rolling(n).std(ddof=0)
    bollinger_down = sma - std * 2
    bollinger_up = sma + std * 2
    band = pandas.concat([bollinger_down, bollinger_up], axis=1)
    band_array = numpy.array(band)
    return band_array


def detect_patterns_in_ohlcs(ohlcs, patterns):
    detected_patterns = [[] for _ in range(len(ohlcs))]
    for pattern in patterns:
        data = pandas.DataFrame(ohlcs)
        num = getattr(talib, pattern)(data[0], data[1], data[2], data[3])
        none_zeros = num[num != 0]
        indexes = list(none_zeros.index)
        for index in indexes:
            pattern_type = str(PATTERNS[pattern]) + '_' + ('BULLISH' if none_zeros[index] > 0 else 'BEARISH')
            pattern_with_prefix = pattern_type + '_' + pattern
            detected_patterns[index].append(pattern_with_prefix)

    return detected_patterns


def notify_in_telegram(message, entity):
    myclient.get_dialogs()
    entity = myclient.get_entity(entity)
    myclient.send_message(entity, message)


def has_trend_changed2short(arr):
    maximum = max(arr)
    if maximum > 0:
        max_index = arr.index(maximum)
        if max_index not in (0, len(arr) - 1):
            max_left = arr[:max_index]
            max_right = arr[max_index + 1:]
            if max_left == sorted(max_left) and max_right == sorted(max_right, reverse=True):
                return True
    return False


def has_trend_changed2long(arr):
    minimum = min(arr)
    if minimum < 0:
        min_index = arr.index(minimum)
        if min_index not in (0, len(arr) - 1):
            min_left = arr[:min_index]
            min_right = arr[min_index + 1:]
            if min_left == sorted(min_left, reverse=True) and min_right == sorted(min_right):
                return True
    return False


@shared_task
def generate_technical_signals():
    global myclient
    if not myclient:
        myclient = create_client()
    datetime_str = datetime.now().strftime("%Y/%m/%d, %H") + ':30'
    notify_in_telegram(datetime_str, 'My logs')
    appropriate_symbols = []
    data_logs = ''
    i = 1
    for symbol in symbols:
        result, data_log = check_symbol_for_signal(symbol)
        data_logs += '\n\n' + data_log
        if result:
            appropriate_symbols.append(symbol)
        if i % 5 == 0 or i == len(symbols):
            notify_in_telegram(data_logs, 'My logs')
            data_logs = ''
        i += 1

    message = 'appropriate symbols:{}\n'.format(appropriate_symbols)
    notify_in_telegram(message, 'My alarms')
    gc.collect()


@catch_all_exceptions()
def check_symbol_for_signal(symbol):
    data = pandas.DataFrame(yf.download(symbol, interval='1h', period='1mo')[:-2])
    data_4h = data.resample('4H', offset='2H').agg(
        OrderedDict([
            ('Open', 'first'),
            ('High', 'max'),
            ('Low', 'min'),
            ('Close', 'last'),
        ]),
    ).dropna()

    ohlcs = data.values.tolist()
    ccis = get_ccis(ohlcs)
    macds = get_macds(data_4h)
    bollinger_bands = get_bollinger_bands(data_4h)
    patterns = detect_patterns_in_ohlcs(ohlcs, PATTERNS)

    logger = my_get_logger()
    data_log = '''
symbol: {},
prev cci: {},
cci: {},
last 4 macds: {},
previous candle patterns: {},
current candle patterns: {},
bbd: {},
bbu: {},
rr: {},
confirmations: {}'''
    cci, prev_cci = ccis[-1], ccis[-2]
    last4macds = macds[-4:]
    macd, prev_macd = last4macds[-1], last4macds[-2]
    bbd, bbu = bollinger_bands[-1]
    current_candle_patterns, previous_candle_patterns = patterns[-1], patterns[-2]
    close = ohlcs[-1][3]

    trend_changed2long = has_trend_changed2long(last4macds) or has_trend_changed2long(last4macds[1:])
    trend_changed2short = has_trend_changed2short(last4macds or has_trend_changed2short(last4macds[1:]))

    data_log = data_log.format(
        symbol,
        prev_cci,
        cci,
        str(last4macds),
        str(previous_candle_patterns),
        str(current_candle_patterns),
        bbd,
        bbu,
        '{}',
        '{}',
    )

    rr = None
    confirmations = None

    watching_signal = FuturesSignal.objects.filter(symbol=symbol, status=FuturesSignal.Status.WATCHING.value).first()
    if watching_signal:
        if cci < -100 or cci > 100:
            watching_signal.status = FuturesSignal.Status.UNWATCHED.value
            watching_signal.save()
            data_log = data_log.format(rr, confirmations)
            data_log += '\nsignal watching status: {}'.format('unwatched')
            return False, data_log
        else:
            if watching_signal.side == 'buy':
                risk = (close - bbd) / close
                reward = (bbu - close) / close
                rr = risk / reward
                if ((macd > 0 and prev_macd > 0) or macd > prev_macd or trend_changed2long) and 0 < rr < 2 \
                        and has_long_candlestick_confirmation(previous_candle_patterns, current_candle_patterns):
                    watching_signal.status = FuturesSignal.Status.WAITING.value
                    watching_signal.confirmations.append('Candlestick')
                    watching_signal.save()
                    data_log = data_log.format(rr, str(watching_signal.confirmations))
                    data_log += '\nsignal watching status: {}'.format('waiting')
                    return True, data_log
                else:
                    data_log = data_log.format(rr, confirmations)
                    return False, data_log
            else:
                risk = (bbu - close) / close
                reward = (close - bbd) / close
                rr = risk / reward
                if ((macd < 0 and prev_macd < 0) or macd < prev_macd or trend_changed2short) and 0 < rr < 2 \
                        and has_short_candlestick_confirmation(previous_candle_patterns, current_candle_patterns):
                    watching_signal.status = FuturesSignal.Status.WAITING.value
                    watching_signal.confirmations.append('Candlestick')
                    watching_signal.save()
                    data_log = data_log.format(rr, str(watching_signal.confirmations))
                    data_log += '\nsignal watching status: {}'.format('waiting')
                    return True, data_log
                else:
                    data_log = data_log.format(rr, confirmations)
                    return False, data_log

    else:

        if prev_cci < -100 < cci or trend_changed2long:
            side = 'buy'
            if prev_cci < -100 < cci:
                confirmations = ['CCI']
                if (macd > 0 and prev_macd > 0) or macd > prev_macd:
                    confirmations.append('Trend')
            if trend_changed2long:
                confirmations = ['Trend']
                if cci > -100 and 'CCI' not in confirmations:
                    confirmations.append('CCI')

            risk = (close - bbd) / close
            reward = (bbu - close) / close
            rr = risk / reward
            if 0 < rr < 2:
                confirmations.append('Bollinger Bands')
            if has_long_candlestick_confirmation(previous_candle_patterns, current_candle_patterns):
                confirmations.append('Candlestick')
            data_log = data_log.format(
                rr,
                str(confirmations),
            )

        elif prev_cci > 100 > cci or trend_changed2short:
            side = 'sell'
            if prev_cci > 100 > cci:
                confirmations = ['CCI']
                if macd < 0 and prev_macd < 0 or macd < prev_macd:
                    confirmations.append('Trend')
            if trend_changed2short:
                confirmations = ['Trend']
                if cci < 100 and 'CCI' not in confirmations:
                    confirmations.append('CCI')

            risk = (bbu - close) / close
            reward = (close - bbd) / close
            rr = risk / reward
            if 0 < rr < 2:
                confirmations.append('Bollinger Bands')
            if has_short_candlestick_confirmation(previous_candle_patterns, current_candle_patterns):
                confirmations.append('Candlestick')
            data_log = data_log.format(
                rr,
                str(confirmations),
            )

        data_log = data_log.format(rr, confirmations)
        logger.debug(data_log)

        if confirmations and all(c in confirmations for c in ['CCI', 'Trend', 'Bollinger Bands']):
            # leverage = min(int(10 / (100 * risk)), 20)
            signal_data = {'symbol': symbol,
                           'side': side,
                           'confirmations': confirmations}
            if 'Candlestick' in confirmations:
                FuturesSignal.objects.create(**signal_data)
                return True, data_log
            else:
                signal_data['status'] = FuturesSignal.Status.WATCHING.value
                FuturesSignal.objects.create(**signal_data)
                data_log += '\nsignal watching status: {}'.format('watching')
                return False, data_log
        return False, data_log
