from .strategy import SpotStrategy
from .signal import Signal


class SpotPosition:
    def __init__(self, signal: Signal, volume: float, strategy: SpotStrategy):
        self.signal = signal
        self.volume = volume
        self.strategy = strategy
