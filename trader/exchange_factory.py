import ccxt.async_support as ccxt


class ExchageFactory:
    @staticmethod
    def create_exchange(id='binance'):
        exchange = getattr(ccxt, id)({
            'enableRateLimit': True,
        })
        return exchange
