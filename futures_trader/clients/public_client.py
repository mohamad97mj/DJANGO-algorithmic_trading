from futures_trader.exchange import ef


class PublicClient:
    def __init__(self, exchange_id):
        self._exchange = ef.create_exchange(exchange_id=exchange_id)

    def fetch_ticker(self, symbol='BTC/USDT'):
        return self._exchange.fetch_ticker(symbol=symbol)

    def get_contracts(self):
        return self._exchange.get_contracts()

    def get_contract(self, symbol):
        return self._exchange.get_contract(symbol=symbol)

    def fetch_status(self):
        return self._exchange.fetch_status()

    def load_markets(self, reload=False):
        return self._exchange.load_markets(reload=reload)

    def get_markets(self):
        return self._exchange.get_markets()
