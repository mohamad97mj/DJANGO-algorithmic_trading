from trader.clients.public_client import PublicClient
from .. import SpotPosition
from .. import SpotStrategy


class SpotStrategyCenter:

    def __init__(self, exchange_id):
        self._public_client = PublicClient(exchange_id)

    def set_strategy_operations(self, position: SpotPosition):
        return strategy_mapper[position.strategy](position=position)

    def set_trailing_stoploss_strategy(self, position: SpotPosition):
        symbol = position.signal.symbol
        # ticker = self._public_client.fetch_ticker(symbol=symbol)
        # print(ticker)
        ohlcv = self._public_client.fetch_ohlcv(symbol=symbol)

    strategy_mapper = {
        'trailing_stoploss': set_trailing_stoploss_strategy,
    }
