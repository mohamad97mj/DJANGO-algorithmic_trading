from .manual_strategy import ManualStrategyDeveloper

strategy_mapper = {
    'manual': ManualStrategyDeveloper,
}


class FuturesStrategyCenter:

    @staticmethod
    def get_strategy_developer(strategy):
        return strategy_mapper[strategy]
