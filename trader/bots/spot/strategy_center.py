from trader.bots.spot.models.position import SpotPosition
from trader.bots.spot.models.strategy import SpotStrategy
from trader.clients.public_client import PublicClient

from typing import List


class SpotStrategyCenter:

    def __init__(self, exchange_id):
        self._public_client = PublicClient(exchange_id)

    def get_strategy(self, strategy_name, position: SpotPosition):
        return strategy_mapper[strategy_name](position=position)

    def get_trailing_stoploss_strategy(self, position: SpotPosition) -> SpotStrategy:
        symbol = position.signal.symbol
        # ticker = self._public_client.fetch_ticker(symbol=symbol)
        # print(ticker)
        ohlcv = self._public_client.fetch_ohlcv(symbol=symbol)

        return SpotStrategy()

    strategy_mapper = {
        'trailing_stoploss': get_trailing_stoploss_strategy,
    }
