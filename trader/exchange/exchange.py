import ccxt.async_support as ccxt


class Exchange:
    def __init__(self, third_party_exchange: ccxt.Exchange):
        self._third_party_exchange = third_party_exchange

    def load_markets(self):
        markets = self._third_party_exchange.load_markets()
        return markets
