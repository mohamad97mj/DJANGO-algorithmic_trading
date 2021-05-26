import ccxt.async_support as ccxt


class ExchageFactory:
    def create_exchange(self, name='binance'):
        exchange = getattr(ccxt, name)({
            'enableRateLimit': True,
        })
        return exchange
