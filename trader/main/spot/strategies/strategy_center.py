from trader.clients.public_client import PublicClient
from trader.main.spot.models import SpotPosition
from .trailing_stoploss_strategy import TrailingStoplossStrategyDeveloper


class SpotStrategyCenter:

    def __init__(self, exchange_id):
        self._public_client = PublicClient(exchange_id)
        self._strategy = None
        self._strategy_mapper = {
            'trailing_stoploss': TrailingStoplossStrategyDeveloper
        }

    def set_strategy(self, strategy):
        self._strategy = self._strategy_mapper[strategy](self._public_client)

    def get_strategy_price_required_symbols(self):
        return self._strategy.get_price_required_symbols()

    def get_strategy_operations(self, position: SpotPosition, strategy_state_data):
        return self._strategy.get_operations(position=position, strategy_state_data=strategy_state_data)
