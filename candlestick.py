import talib
import pandas as pd
import json
from datetime import datetime, timedelta
from pprint import pprint

from spot_trader.clients.public_client import PublicClient as SpotPublicClient
from fetch import symbols

PATTERNS = {
    'CDL2CROWS': 1,  # Two Crows,
    'CDL3BLACKCROWS': 3,  # Three Black Crows,
    'CDL3INSIDE': 2,  # Three Inside Up/Down,
    # 'CDL3LINESTRIKE': 1 or 3,  # Three-Line Strike,
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
    # 'CDLHIKKAKE': 1,  # Hikkake Pattern,
    # 'CDLHIKKAKEMOD': 1,  # Modified Hikkake Pattern,
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


def detect_patterns_in_ohlcvs(ohlcvs, patterns):
    detected_patterns = {}
    for pattern in patterns:
        data = pd.DataFrame(ohlcvs)
        num = getattr(talib, pattern)(data[1], data[2], data[3], data[4])
        none_zeros = num[num != 0]
        indexes = list(none_zeros.index)
        for index in indexes:
            # date = datetime.fromtimestamp(int(data.iloc[index][0] / 1000)).strftime("%m/%d/%Y, %H:%M:%S")
            date = int(data.iloc[index][0] / 1000)
            pattern_type = str(PATTERNS[pattern]) + '_' + ('BULLISH' if none_zeros[index] > 0 else 'BEARISH')
            pattern_with_prefix = pattern_type + '_' + pattern
            if date in detected_patterns:
                detected_patterns[date].append(pattern_with_prefix)
            else:
                detected_patterns[date] = [pattern_with_prefix]
    sorted_detected_patterns_by_date = dict(sorted(detected_patterns.items()))
    date_converted_detected_patterns = {
        datetime.fromtimestamp(timestamp).strftime("%m/%d/%Y, %H:%M:%S"): sorted_detected_patterns_by_date[timestamp]
        for timestamp in sorted_detected_patterns_by_date}
    return date_converted_detected_patterns


def detect_patterns():
    detected_patterns = {}
    spot_public_client = SpotPublicClient()
    for symbol in symbols:
        ohlcvs = spot_public_client.fetch_ohlcv(symbol=symbol, timeframe='1h', limit=1000)
        detected_patterns[symbol] = detect_patterns_in_ohlcvs(ohlcvs, PATTERNS.keys())
    f = open('candlestick.txt', 'w')
    f.write(json.dumps(detected_patterns, indent=3))


def detect_patterns_at_datetime(symbol, date: datetime):
    since = int((date - timedelta(hours=20)).timestamp() * 1000)
    spot_public_client = SpotPublicClient()
    ohlcvs = spot_public_client.fetch_ohlcv(symbol=symbol, timeframe='1h', since=since, limit=21)
    return detect_patterns_in_ohlcvs(ohlcvs=ohlcvs, patterns=PATTERNS.keys())


def detect_patterns_in_current_and_previous_candles(symbol):
    now = datetime.now()
    detected_patterns = detect_patterns_at_datetime(symbol, now)
    now_minus_30 = now - timedelta(minutes=30)
    now_rounded = datetime(year=now_minus_30.year, month=now_minus_30.month, day=now_minus_30.day,
                           hour=now_minus_30.hour, minute=30)
    now_rounded_str = now_rounded.strftime("%m/%d/%Y, %H:%M:%S")
    one_hour_ago = now_rounded - timedelta(hours=1)
    one_hour_ago_str = one_hour_ago.strftime("%m/%d/%Y, %H:%M:%S")
    return detected_patterns.get(one_hour_ago_str, []), detected_patterns.get(now_rounded_str, [])


def detect_patterns_in_two_previous_candles(symbol):
    now = datetime.now()
    detected_patterns = detect_patterns_at_datetime(symbol, now)
    now_minus_1_30 = now - timedelta(hours=1, minutes=30)
    one_our_ago_rounded = datetime(year=now_minus_1_30.year, month=now_minus_1_30.month, day=now_minus_1_30.day,
                                   hour=now_minus_1_30.hour, minute=30)
    one_hour_ago_rounded_str = one_our_ago_rounded.strftime("%m/%d/%Y, %H:%M:%S")
    two_hour_ago = one_our_ago_rounded - timedelta(hours=1)
    two_hour_ago_str = two_hour_ago.strftime("%m/%d/%Y, %H:%M:%S")
    return detected_patterns.get(two_hour_ago_str, []), detected_patterns.get(one_hour_ago_rounded_str, [])


def detect_patterns_in_current_and_previous_candles_for_all_symbols():
    detected_patterns = {}
    for symbol in symbols:
        detected_patterns[symbol] = detect_patterns_in_current_and_previous_candles(symbol)
    f = open('candlestick_now.txt', 'w')
    f.write(json.dumps(detected_patterns, indent=3))


def detect_patterns_in_two_previous_candles_for_all_symbols():
    detected_patterns = {}
    for symbol in symbols:
        detected_patterns[symbol] = detect_patterns_in_two_previous_candles(symbol)
    f = open('candlestick_previous.txt', 'w')
    f.write(json.dumps(detected_patterns, indent=3))


def get_pattern_weight(pattern):
    strength, type_, _ = pattern.split('_')
    sign = 1 if type_ == 'BULLISH' else -1
    return int(strength) * sign


def get_candle_type(patterns):
    weights = [get_pattern_weight(pattern) for pattern in patterns]
    reliable_or_strong_weights = filter(lambda x: x > 1 or x < -1, weights)
    weights_sum = sum(weights)
    reliable_or_strong_weights_sum = sum(reliable_or_strong_weights)
    if weights_sum == 0:
        return 0
    elif weights_sum > 0:
        if reliable_or_strong_weights_sum < 0:
            return 0
        elif reliable_or_strong_weights_sum == 0:
            if weights_sum <= 3:
                return 1
            else:
                return 2
        else:
            if weights_sum == 1:
                return 1
            elif weights_sum <= 3:
                return 2
            else:
                return 3
    else:
        if reliable_or_strong_weights_sum > 0:
            return 0
        elif reliable_or_strong_weights_sum == 0:
            if weights_sum >= -3:
                return -1
            else:
                return -2
        else:
            if weights_sum == -1:
                return -1
            elif weights_sum >= -3:
                return -2
            else:
                return -3


def has_long_candlestick_confirmation(previous_candle_patterns, current_candle_patterns):
    if get_candle_type(current_candle_patterns) > 0 and \
            get_candle_type(current_candle_patterns) + get_candle_type(previous_candle_patterns) > 0:
        return True
    return False


def has_short_candlestick_confirmation(previous_candle_patterns, current_candle_patterns):
    if get_candle_type(current_candle_patterns) < 0 and \
            get_candle_type(current_candle_patterns) + get_candle_type(previous_candle_patterns) < 0:
        return True
    return False
