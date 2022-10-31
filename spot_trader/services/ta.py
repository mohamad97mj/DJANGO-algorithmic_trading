import numpy
import pandas
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from math import nan

from ..clients.public_client import PublicClient
from futures_trader.clients.public_client import PublicClient as FuturesPublicClient

pb = PublicClient()


class TechnicalAnalyser:

    @staticmethod
    def get_ccis(symbol, timeframe='1h', n=20, ohlcvs=None, limit=40):
        if not ohlcvs:
            ohlcvs = pb.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if ohlcvs:
            np_array = numpy.array(ohlcvs)
            open_prices = pandas.Series(np_array[:, 1])
            high_prices = pandas.Series(np_array[:, 2])
            low_prices = pandas.Series(np_array[:, 3])
            close_prices = pandas.Series(np_array[:, 4])

            # close_prices_ha = (open_prices + high_prices + low_prices + close_prices) / 4
            # open_prices_ha = (open_prices[0: -1] + close_prices[0: -1]) / 2

            # TP = (high_prices + low_prices + close_prices_ha) / 3
            TP = (high_prices + low_prices + close_prices) / 3
            sma = TP.rolling(n).mean()
            mad = TP.rolling(n).apply(lambda x: pandas.Series(x).mad())
            CCI = (TP - sma) / (0.015 * mad)
            CCI_list = CCI.to_list()
            # return CCI_list
            return CCI_list

    @staticmethod
    def get_cci(symbol, timeframe='1h', n=20, ohlcvs=None):
        ccis = TechnicalAnalyser.get_ccis(symbol, timeframe, n, ohlcvs=ohlcvs, limit=n + 1)
        if ccis:
            return ccis[-1], ccis[-2]
        return None, None

    @staticmethod
    def get_two_previous_cci(symbol, timeframe='1h', n=20, ohlcvs=None):
        ccis = TechnicalAnalyser.get_ccis(symbol, timeframe, n, ohlcvs=ohlcvs, limit=n + 5)
        if ccis:
            if ccis[-3] and ccis[-3] != nan:
                return ccis[-2], ccis[-3]
            elif ccis[-2] and ccis[-2] != nan:
                return ccis[-1], ccis[-2]
            else:
                return TechnicalAnalyser.get_two_previous_cci(symbol)
        return None, None

    @staticmethod
    def get_heikin_ashi_candles(symbol, timeframe, last_open, ohlcvs=None):
        if not ohlcvs:
            ohlcvs = pb.fetch_ohlcv(symbol, timeframe=timeframe)
        if ohlcvs:
            np_array = numpy.array(ohlcvs)
            open_prices = pandas.Series(np_array[:, 1])
            high_prices = pandas.Series(np_array[:, 2])
            low_prices = pandas.Series(np_array[:, 3])
            close_prices = pandas.Series(np_array[:, 4])
            open_prices_ha = [0] * len(ohlcvs)
            open_prices_ha[-1] = last_open

            close_prices_ha = round((open_prices + high_prices + low_prices + close_prices) / 4, 1)
            for i in range(len(ohlcvs) - 2, -1, -1):
                x = open_prices_ha[i + 1]
                y = close_prices_ha[i]
                open_prices_ha[i] = round(2 * open_prices_ha[i + 1] - close_prices_ha[i], 1)
            candle = pandas.concat([pandas.Series(open_prices_ha), close_prices_ha], axis=1)
            candle_array = numpy.array(candle)
            return candle_array

    @staticmethod
    def get_rsi(symbol, timeframe):
        ohlcvs = pb.fetch_ohlcv(symbol, timeframe=timeframe)
        if ohlcvs:
            np_array = numpy.array(ohlcvs)
            close_prices = pandas.Series(np_array[:, 4])
            rsi_14 = RSIIndicator(close=close_prices, window=14).rsi().tolist()[-1]
            return rsi_14

    @staticmethod
    def get_bollinger_bands(symbol, timeframe='4h', n=20, ohlcvs=None, limit=20):
        if not ohlcvs:
            ohlcvs = pb.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        np_array = numpy.array(ohlcvs)
        sma = TechnicalAnalyser.get_sma(symbol, timeframe, n, ohlcvs)
        close_prices = pandas.Series(np_array[:, 4])
        std = close_prices.rolling(n).std(ddof=0)
        bollinger_down = sma - std * 2
        bollinger_up = sma + std * 2  # Calculate top band
        band = pandas.concat([bollinger_down, bollinger_up], axis=1)
        band_array = numpy.array(band)
        return band_array

    @staticmethod
    def get_bollinger_band(symbol, timeframe='4h', n=20, ohlcvs=None):
        bollinger_bands = TechnicalAnalyser.get_bollinger_bands(symbol, timeframe, n, ohlcvs, limit=n + 1)
        return bollinger_bands[-1]

    @staticmethod
    def get_sma(symbol, timeframe, n, ohlcvs=None):
        if not ohlcvs:
            ohlcvs = pb.fetch_ohlcv(symbol, timeframe=timeframe)
        np_array = numpy.array(ohlcvs)
        close_prices = pandas.Series(np_array[:, 4])
        return close_prices.rolling(n).mean()

    @staticmethod
    def get_ema(symbol, timeframe, n, ohlcvs=None):
        if not ohlcvs:
            ohlcvs = pb.fetch_ohlcv(symbol, timeframe=timeframe)
        np_array = numpy.array(ohlcvs)
        close_prices = pandas.Series(np_array[:, 4])
        ema = EMAIndicator(close=close_prices, window=n)
        return ema

    @staticmethod
    def find_lowest_rsi(timeframe='15m'):
        public_client = FuturesPublicClient()
        symbols = public_client.load_markets()
        rsi_values = []
        for symbol in symbols:
            rsi_value = TechnicalAnalyser.get_rsi(symbol, timeframe)
            if rsi_value:
                rsi_values.append((symbol, rsi_value))
        sorted_rsi_values = sorted(rsi_values, key=lambda v: v[1])
        print(sorted_rsi_values)

    @staticmethod
    def get_macds(symbol, timeframe='4h', ohlcvs=None, limit=40):
        if not ohlcvs:
            ohlcvs = pb.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if ohlcvs:
            np_array = numpy.array(ohlcvs)
            close_prices = pandas.Series(np_array[:, 4])
            macd = MACD(close=close_prices)
            return macd.macd_diff().tolist()

    @staticmethod
    def get_macd(symbol, timeframe='4h', ohlcvs=None):
        macds = TechnicalAnalyser.get_macds(symbol, timeframe, ohlcvs=ohlcvs)
        return macds[-1], macds[-2]

    @staticmethod
    def get_last4macds(symbol, timeframe='4h', ohlcvs=None):
        macds = TechnicalAnalyser.get_macds(symbol, timeframe, ohlcvs=ohlcvs)
        return macds[-4:]
