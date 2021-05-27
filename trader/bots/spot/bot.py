from trader.exchange import Exchange
from .models import SpotPosition
from .strategy_center import SpotStrategyCenter


class SpotBot:
    def __init__(self, exchange: Exchange, position: SpotPosition, strategy_id: str):
        self._exchange = exchange
        self._position = position
        self._strategy = SpotStrategyCenter.get_strategy(strategy_id)

    def run(self):
        self._strategy = SpotStrategyCenter.get_trailing_stoploss_strategy()
