from trader.main.futures.exchange import ef


class PublicClient:
    def __init__(self, exchange_id):
        self._exchange = ef.create_exchange(exchange_id=exchange_id)

    def fetch_ticker(self, symbol='BTC/USDT'):
        return self._exchange.fetch_ticker(symbol=symbol)

    def get_contracts(self):
        return self._exchange.get_contracts()

    def get_contract(self, symbol):
        return self._exchange.get_contract(symbol=symbol)
