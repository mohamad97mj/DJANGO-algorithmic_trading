from trader.clients.public_client import PublicClient
from trader.main.spot.models import SpotPosition
from .trailing_stoploss_strategy import TrailingStoplossStrategyDeveloper


class SpotStrategyCenter:

    def __init__(self, exchange_id):
        self._public_client = PublicClient(exchange_id)
        self._trailing_stoploss_strategy_developer = TrailingStoplossStrategyDeveloper(self._public_client)

        self._strategy_mapper = {
            'trailing_stoploss': self._trailing_stoploss_strategy_developer.set_operations,
        }

    def set_strategy_operations(self, strategy: str, position: SpotPosition, strategy_state_data):
        return self._strategy_mapper[strategy](position=position, strategy_state_data=strategy_state_data)
