from .manual_strategy import ManualStrategyDeveloper

strategy_mapper = {
    'manual': ManualStrategyDeveloper,
}


class SpotStrategyCenter:

    @staticmethod
    def get_strategy_developer(strategy):
        return strategy_mapper[strategy]
