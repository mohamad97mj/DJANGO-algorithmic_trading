import numpy as np
from trader.clients.public_client import PublicClient
from trader.main.spot.models import SpotPosition


class SpotStrategyCenter:

    def __init__(self, exchange_id):
        self._trailing_stoploss_strategy_developer = TrailingStoplossStrategyDeveolper(exchange_id)

        self._strategy_mapper = {
            'trailing_stoploss': self._trailing_stoploss_strategy_developer.set_operations,
        }
        self._public_client = PublicClient(exchange_id)

    def set_strategy_operations(self, strategy: str, position: SpotPosition):
        return self._strategy_mapper[strategy](position=position)

