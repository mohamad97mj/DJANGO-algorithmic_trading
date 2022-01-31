import numpy
import pandas
from ta.momentum import RSIIndicator

from ..clients.public_client import PublicClient
from futures_trader.clients.public_client import PublicClient as FuturesPublicClient


class TechnicalAnalyser:
    @staticmethod
    def get_rsi(symbol, timeframe):
        pb = PublicClient()
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


