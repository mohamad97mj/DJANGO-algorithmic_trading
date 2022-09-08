import pandas as pd
import plotly.graph_objects as go
import numpy as np
from matplotlib import pyplot
from ast import literal_eval


def plot_chart():
    backcandles = 100
    brange = 80
    wind = 5
    candleid = 350
    symbol = 'BTCUSDT'
    f = open("data/ohlcv/{}.txt".format(symbol.replace('/', '')), "r")
    ohlcvs = f.readline()
    ohlcv_list = literal_eval(ohlcvs)
    df = pd.DataFrame(ohlcv_list, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    partial_df = df[candleid - backcandles: candleid + backcandles]
    sldiff = 5
    sldist = 10000
    is_first = True
    for r1 in range(backcandles - brange, backcandles + brange):
        maxim = np.array([])
        minim = np.array([])
        xxmin = np.array([])
        xxmax = np.array([])

        for i in range(candleid - r1, candleid + 1, wind):
            minim = np.append(minim, df.low.iloc[i:i + wind].min())
            xxmin = np.append(xxmin, df.low.iloc[i:i + wind].idxmin())

        for i in range(candleid - r1, candleid + 1, wind):
            maxim = np.append(maxim, df.high.iloc[i: i + wind].min())
            xxmax = np.append(xxmax, df.high.iloc[i: i + wind].idxmax())

        slmin, intercmin = np.polyfit(xxmin, minim, 1)
        slmax, intercmax = np.polyfit(xxmax, maxim, 1)
        dist = (slmax * candleid + intercmax) - (slmin * candleid + intercmin)
        if dist < sldist:
            sldiff = abs(slmin - slmax)
            if sldiff <= 10 or is_first:
                if is_first:
                    is_first = False
                sldist = dist
                optbackcandles = r1
                slminopt = slmin
                slmaxopt = slmax
                intercminopt = intercmin
                intercmaxopt = intercmax
                maximopt = maxim.copy()
                minimopt = minim.copy()
                xxminopt = xxmin.copy()
                xxmaxopt = xxmax.copy()

    fig = go.Figure(data=[go.Candlestick(x=partial_df.index,
                                         open=partial_df['open'],
                                         high=partial_df['high'],
                                         low=partial_df['low'],
                                         close=partial_df['close'])])
    adjintercmax = (df.high.iloc[xxmaxopt] - slmaxopt * xxmaxopt).max()
    adjintercmin = (df.low.iloc[xxminopt] - slminopt * xxminopt).min()
    fig.add_trace(go.Scatter(x=xxminopt, y=slminopt * xxminopt + adjintercmin, mode='lines', name='min slope'))
    fig.add_trace(go.Scatter(x=xxmaxopt, y=slmaxopt * xxmaxopt + adjintercmax, mode='lines', name='max slope'))
    fig.show()
