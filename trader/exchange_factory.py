import ccxt.async_support as ccxt
from .auth import credentials


class ExchageFactory:
    @staticmethod
    def create_exchange(id='binance', credential='test'):
        exchange = getattr(ccxt, id)({
            'apiKey': credentials[credential]['api_key'],
            'secret': credentials[credential]['secret_key'],
            'timeout': 30000,
            'enableRateLimit': True,
        })
        return exchange
