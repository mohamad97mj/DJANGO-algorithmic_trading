from trader.bots.spot.models.position import SpotPosition
from trader.bots.spot.models.strategy import SpotStrategy
from trader.clients.public_client import PublicClient

from typing import List


class SpotStrategyCenter:

    def __init__(self, exchange_id):
        self._public_client = PublicClient(exchange_id)

    @staticmethod
    def get_strategy(strategy_name, position: SpotPosition):
        return strategy_mapper[strategy_name](position)

    @staticmethod
    def get_trailing_stoploss_strategy(position: SpotPosition) -> SpotStrategy:
        kindles = self._public_client.fetch_ticker()
        print(kindles)

        return SpotStrategy()


strategy_mapper = {
    'trailing_stoploss': SpotStrategyCenter.get_trailing_stoploss_strategy,
}
