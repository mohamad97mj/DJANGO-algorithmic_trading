import numpy as np
import pandas as pd
import matplotlib.dates as mdates

from spot_trader.clients.public_client import PublicClient as SpotPublicClient
from dataclasses import dataclass
from enum import Enum

from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpl_dates
import matplotlib.pyplot as plt


@dataclass
class SRLevel:
    class Type(Enum):
        SUPPORT = 1
        RESISTANCE = 2

    type: int
    idx: float
    value: float


@dataclass
class SRZone:
    lower_level: SRLevel = None
    upper_level: SRLevel = None


spot_public_client = SpotPublicClient()


def is_far_from_next_level(level, nex_level, ave):
    return nex_level.value - level.value > ave


def detect_sr_zones(symbol):
    ohlcvs = spot_public_client.fetch_ohlcv(symbol=symbol, timeframe='1h', limit=360)
    data = pd.DataFrame(ohlcvs)
    return detect_sr_zones_in_data_frame(data)


def detect_and_plot_sr_zones(symbol):
    ohlcvs = spot_public_client.fetch_ohlcv(symbol=symbol, timeframe='1h', limit=360)
    data = pd.DataFrame(ohlcvs)[:-1]
    data[0] = mdates.epoch2num(data[0] / 1000)
    zones = detect_sr_zones(symbol)
    plot_all(zones, data)


def detect_and_plot_sr_zones_for_all_symbols():
    from fetch import symbols
    for symbol in symbols:
        detect_and_plot_sr_zones(symbol)


def detect_sr_zones_in_data_frame(data):
    highs = data[2]
    lows = data[3]
    levels = detect_sr_levels(highs, lows)
    sorted_levels = sorted(levels, key=lambda l: l.value)
    ave = np.mean(highs - lows) * 0.75
    sr_zones = []
    previous_near_level = None
    for i in range(len(sorted_levels) - 2):
        if is_far_from_next_level(sorted_levels[i], sorted_levels[i + 1], ave):
            sr_zones.append(SRZone(lower_level=previous_near_level, upper_level=sorted_levels[i]))
            previous_near_level = None
        else:
            if not previous_near_level:
                previous_near_level = sorted_levels[i]
    sr_zones.append(SRZone(lower_level=previous_near_level, upper_level=sorted_levels[-1]))
    return sr_zones


def detect_sr_levels(highs, lows):
    levels = []
    max_list = []
    min_list = []
    window_size = 18
    for i in range(window_size, len(highs) - window_size):
        high_range = highs[i - window_size:i + window_size - 1]
        current_max = high_range.max()
        if current_max not in max_list:
            max_list = []
        max_list.append(current_max)
        if len(max_list) == window_size:
            levels.append(SRLevel(SRLevel.Type.RESISTANCE.value, high_range.idxmax(), current_max))

        low_range = lows[i - window_size:i + window_size - 1]
        current_min = low_range.min()
        if current_min not in min_list:
            min_list = []
        min_list.append(current_min)
        if len(min_list) == window_size:
            levels.append(SRLevel(SRLevel.Type.SUPPORT.value, low_range.idxmin(), current_min))

    return levels


# for visualization
def plot_all(zones, data):
    fig, ax = plt.subplots(figsize=(16, 9))
    candlestick_ohlc(ax, data.values, width=0.05, colorup='green', colordown='red', alpha=0.8)
    date_format = mpl_dates.DateFormatter('%d %b %Y')
    ax.xaxis.set_major_formatter(date_format)
    for zone in zones:
        lower_level = zone.lower_level
        upper_level = zone.upper_level
        if lower_level and upper_level:
            plt.axhspan(lower_level.value, upper_level.value)
        else:
            if lower_level:
                plt.hlines(lower_level.value, xmin=min(data[0]), xmax=max(data[0]), colors='blue', linestyle='--')
            if upper_level:
                plt.hlines(upper_level.value, xmin=min(data[0]), xmax=max(data[0]), colors='blue', linestyle='--')
    fig.show()
