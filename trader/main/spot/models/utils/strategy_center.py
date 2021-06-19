from trader.clients.public_client import PublicClient
from .. import SpotPosition


class SpotStrategyCenter:

    def __init__(self, exchange_id):
        self.strategy_mapper = {
            'trailing_stop_loss': self.set_trailing_stoploss_strategy,
        }
        self._public_client = PublicClient(exchange_id)

    def set_strategy_operations(self, position: SpotPosition):
        return self.strategy_mapper[position.strategy](position=position)

    def set_trailing_stoploss_strategy(self, position: SpotPosition):
        symbol = position.signal.symbol
        # ticker = self._public_client.fetch_ticker(symbol=symbol)
        # print(ticker)
        ohlcv = self._public_client.fetch_ohlcv(symbol=symbol)
