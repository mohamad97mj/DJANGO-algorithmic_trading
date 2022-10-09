from datetime import datetime
from fetch import symbols
from ast import literal_eval
from dataclasses import dataclass
from spot_trader.services.ta import TechnicalAnalyser
from global_utils import utc2local
from pprint import pprint


def one2four(arr):
    result = []
    for i in arr:
        for j in range(4):
            result.append(i)
    return result


def read_strategy_data():
    records = {}

    for symbol in symbols:
        f = open("data/ohlcv/{}.txt".format(symbol.replace('/', '')), "r")
        ohlcvs = f.readline()
        ohlcv_list = literal_eval(ohlcvs)
        ccis = TechnicalAnalyser.get_ccis(symbol=symbol, timeframe='1h', n=20, ohlcvs=ohlcv_list)[:-1]
        bb = TechnicalAnalyser.get_bollinger_bands(symbol=symbol, timeframe='1h', n=20, ohlcvs=ohlcv_list)[:-1]
        macd = one2four(TechnicalAnalyser.get_macds(symbol=symbol, timeframe='4h', limit=180))[:-1]
        ohlcvs_filtered = [[datetime.fromtimestamp(int(ohlcv[0]) / 1000), ohlcv[2], ohlcv[3], ohlcv[4]]
                           for ohlcv in ohlcv_list[:-1]]
        for i in range(len(ohlcvs_filtered)):
            ohlcvs_filtered[i].append(ccis[i])
            ohlcvs_filtered[i].append(bb[i][0])
            ohlcvs_filtered[i].append(bb[i][1])
            ohlcvs_filtered[i].append(macd[i])
        records[symbol] = ohlcvs_filtered
    return records


@dataclass
class Position:
    opened_at: datetime
    macd: float
    direction: str
    risk: float
    reward: float
    rr: float
    step: float
    stoploss: float
    tp1: float
    tp2: float
    is_stoploss_trailed: bool = False
    closed_at: datetime = None
    status: str = None


def run():
    positions = {}
    records = read_strategy_data()
    for symbol in symbols:
        positions[symbol] = []
        open_position = None
        for i in range(20, len(records[symbol])):
            record = records[symbol][i]
            date = record[0]
            high = record[1]
            low = record[2]
            close = record[3]
            cci = record[4]
            bb_d = record[5]
            bb_u = record[6]
            macd = record[7]
            prv_cci = records[symbol][i - 1][4]
            # prv_macd = records[symbol][i - 1][7]
            is_long = prv_cci < -100 < cci and macd > 0
            is_short = prv_cci > 100 > cci and macd < 0

            if open_position:
                if open_position.direction == 'long':
                    if is_short:
                        open_position.status = 'c'
                        open_position.closed_at = date
                        open_position = None
                    else:
                        if high > open_position.tp2:
                            open_position.status = 'tp2'
                            open_position.closed_at = date
                            open_position = None
                        elif high > open_position.tp1 and not open_position.is_stoploss_trailed:
                            open_position.status = 'tp1'
                            open_position.stoploss = open_position.step
                            open_position.is_stoploss_trailed = True
                        elif low < open_position.stoploss:
                            if open_position.is_stoploss_trailed:
                                open_position.status = 'tsl'
                            else:
                                open_position.status = 'sl'
                            open_position.closed_at = date
                            open_position = None
                else:
                    if is_long:
                        open_position.status = 'c'
                        open_position.closed_at = date
                        open_position = None
                    else:
                        if low < open_position.tp2:
                            open_position.status = 'tp2'
                            open_position.closed_at = date
                            open_position = None
                        elif low < open_position.tp1 and not open_position.is_stoploss_trailed:
                            open_position.status = 'tp1'
                            open_position.stoploss = open_position.step
                            open_position.is_stoploss_trailed = True
                        elif high > open_position.stoploss:
                            if open_position.is_stoploss_trailed:
                                open_position.status = 'tsl'
                            else:
                                open_position.status = 'sl'
                            open_position.closed_at = date
                            open_position = None
            else:
                if is_long or is_short:
                    if is_long:
                        direction = 'long'
                        sign = 1
                        risk = (close - bb_d) / close
                        reward = (bb_u - close) / close
                    else:
                        direction = 'short'
                        sign = -1
                        risk = (bb_u - close) / close
                        reward = (close - bb_d) / close
                    tp1 = close * (1 + 1 * sign * risk)
                    tp2 = close * (1 + 2 * sign * risk)
                    stoploss = close * (1 - sign * risk)
                    rr = risk / reward
                    # if 0 < rr < 1 / 3:
                    if True:
                        open_position = Position(opened_at=date,
                                                 macd=macd,
                                                 direction=direction,
                                                 risk=risk,
                                                 reward=reward,
                                                 rr=rr,
                                                 step=close,
                                                 stoploss=stoploss,
                                                 tp1=tp1,
                                                 tp2=tp2,
                                                 status='open')
                        positions[symbol].append(open_position)
    return positions


def run2():
    positions = {}
    records = read_strategy_data()
    for symbol in symbols:
        positions[symbol] = []
        open_position = None
        for i in range(20, len(records[symbol])):
            record = records[symbol][i]
            date = record[0]
            high = record[1]
            low = record[2]
            close = record[3]
            cci = record[4]
            bb_d = record[5]
            bb_u = record[6]
            macd = record[7]
            prv_cci = records[symbol][i - 1][4]
            is_long = prv_cci < -100 < cci and macd > 0
            is_short = prv_cci > 100 > cci and macd < 0

            if open_position:
                if open_position.direction == 'long':
                    if is_short:
                        open_position.status = 'c'
                        open_position.closed_at = date
                        open_position = None
                    else:
                        if high > open_position.tp2:
                            open_position.status = 'tp2'
                            open_position.closed_at = date
                            open_position = None
                        elif low < open_position.stoploss:
                            open_position.status = 'sl'
                            open_position.closed_at = date
                            open_position = None
                else:
                    if is_long:
                        open_position.status = 'c'
                        open_position.closed_at = date
                        open_position = None
                    else:
                        if low < open_position.tp2:
                            open_position.status = 'tp2'
                            open_position.closed_at = date
                            open_position = None
                        elif high > open_position.stoploss:
                            open_position.status = 'sl'
                            open_position.closed_at = date
                            open_position = None
            else:
                if is_long or is_short:
                    if is_long:
                        direction = 'long'
                        sign = 1
                        risk = (close - bb_d) / close
                        reward = (bb_u - close) / close
                    else:
                        direction = 'short'
                        sign = -1
                        risk = (bb_u - close) / close
                        reward = (close - bb_d) / close
                    tp1 = close * (1 + 1 * sign * risk)
                    tp2 = close * (1 + 2 * sign * risk)
                    stoploss = close * (1 - 1 * sign * risk)
                    rr = risk / reward
                    if 0 < rr < 1 / 3:
                        open_position = Position(opened_at=date,
                                                 macd=macd,
                                                 direction=direction,
                                                 risk=risk,
                                                 reward=reward,
                                                 rr=rr,
                                                 step=close,
                                                 stoploss=stoploss,
                                                 tp1=tp1,
                                                 tp2=tp2,
                                                 status='open')
                        positions[symbol].append(open_position)
    return positions


def statistic():
    positions = run()
    pprint(positions)
    symbol_statistics = []
    statistics = {
        'sl': 0,
        'tsl': 0,
        'tp1': 0,
        'tp2': 0,
        'c': 0,
        'open': 0
    }
    for symbol in symbols:
        symbol_statistic = {'symbol': symbol,
                            'sl': 1,
                            'tsl': 0,
                            'tp1': 0,
                            'tp2': 1,
                            'c': 0,
                            'open': 0}
        symbol_statistics.append(symbol_statistic)
        for position in positions[symbol]:
            symbol_statistic[position.status] += 1
            statistics[position.status] += 1

    pprint(sorted(symbol_statistics, key=lambda dic: dic['tp2'] / dic['sl'], reverse=True))
    print(statistics)

    # pprint(positions['LINK/USDT'])
