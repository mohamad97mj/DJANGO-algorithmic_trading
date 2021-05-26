from trader.exchange.exchange_factory import ExchageFactory


class SpotTrader:
    def __init__(self, exchange_id):
        self._exchange = ExchageFactory.create_exchange(exchange_id=exchange_id)
