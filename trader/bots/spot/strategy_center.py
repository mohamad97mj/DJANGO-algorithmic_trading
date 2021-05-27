from .models.position import SpotPosition
from .models.order import SpotOrder
from typing import List


class SpotStrategyCenter:

    @staticmethod
    def get_strategy(strategy_id, position: SpotPosition):
        return strategy_mapper[strategy_id](position)

    @staticmethod
    def get_trailing_stoploss_strategy(position: SpotPosition) -> List[SpotOrder]:
        return [
            SpotOrder(),
        ]


strategy_mapper = {
    'trailing_stoploss': SpotStrategyCenter.get_trailing_stoploss_strategy,

}
