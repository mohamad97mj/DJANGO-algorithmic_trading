from trader.client import client
from pprint import pprint
from trader.global_utils import apply2all_methods, log
from binance.client import Client


@apply2all_methods(log)
class MarketDataBot:

    def get_recent_trades(self, symbol='BTCUSDT'):
        trades = client.get_recent_trades(symbol=symbol)
        pprint(trades)
        return trades

    def get_symbol_avg_price(self, symbol='BTCUSDT'):
        avg_price = client.get_avg_price(symbol=symbol)
        pprint(avg_price)
        return avg_price

    def get24hr_ticker(self):
        tickers = client.get_ticker()
        pprint(tickers)
        return tickers

    def get_all_prices(self):
        info = client.get_all_tickers()
        pprint(info)
        return info

    def get_candles(self, symbol='BTCUSDT'):
        candles = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_30MINUTE)
        pprint(candles)
        return candles
