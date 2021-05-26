import ccxt.async_support as ccxt
from trader.auth import credentials
from .exchange import Exchange


class ExchageFactory:
    @staticmethod
    def create_exchange(exchange_id='binance',
                        credential_id='test',
                        enable_rate_limit=True,
                        sandbox_mode=True):
        exchange = getattr(ccxt, exchange_id)({
            'apiKey': credentials[credential_id]['api_key'],
            'secret': credentials[credential_id]['secret_key'],
            'enableRateLimit': enable_rate_limit,
        })
        exchange.set_sandbox_mode(sandbox_mode)
        return Exchange()
