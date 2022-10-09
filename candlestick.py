import talib
import pandas as pd
from datetime import datetime
from spot_trader.clients.public_client import PublicClient as SpotPublicClient
from fetch import symbols


def detect_patterns():
    spot_public_client = SpotPublicClient()
    for symbol in symbols:
        raw_data = spot_public_client.fetch_ohlcv(symbol=symbol, timeframe='1h', limit=1000)
        data = pd.DataFrame(raw_data)
        # num = talib.CDLMORNINGSTAR(data[1], data[2], data[3], data[4])
        num = talib.CDL3LINESTRIKE(data[1], data[2], data[3], data[4])
        none_zeros = num[num != 0]
        indexes = list(none_zeros.index)
        dates = [datetime.fromtimestamp(int(data.iloc[index][0] / 1000)) for index in indexes]
        print(dates)
