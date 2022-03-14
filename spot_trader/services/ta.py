import numpy
import pandas
from ta.momentum import RSIIndicator

from ..clients.public_client import PublicClient
from futures_trader.clients.public_client import PublicClient as FuturesPublicClient

pb = PublicClient()


class TechnicalAnalyser:

    @staticmethod
    def get_cci(symbol, timeframe, n):
        ohlcvs = pb.fetch_ohlcv(symbol, timeframe=timeframe)
        np_array = numpy.array(ohlcvs)
        open_prices = pandas.Series(np_array[:, 1])
        high_prices = pandas.Series(np_array[:, 2])
        low_prices = pandas.Series(np_array[:, 3])
        close_prices = pandas.Series(np_array[:, 4])

        close_prices_ha = (open_prices + high_prices + low_prices + close_prices) / 4
        # open_prices_ha = (open_prices[0: -1] + close_prices[0: -1]) / 2

        TP = (high_prices + low_prices + close_prices_ha) / 3
        sma = TP.rolling(n).mean()
        mad = TP.rolling(n).apply(lambda x: pandas.Series(x).mad())
        CCI = (TP - sma) / (0.015 * mad)
        CCI_list = CCI.to_list()
        return CCI_list[-1]

    @staticmethod
    def get_rsi(symbol, timeframe):
        ohlcvs = pb.fetch_ohlcv(symbol, timeframe=timeframe)
        if ohlcvs:
            np_array = numpy.array(ohlcvs)
            close_prices = pandas.Series(np_array[:, 4])
            rsi_14 = RSIIndicator(close=close_prices, window=14).rsi().tolist()[-1]
            return rsi_14

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
