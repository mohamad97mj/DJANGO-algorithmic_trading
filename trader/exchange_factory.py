import ccxt.async_support as ccxt
from .auth import credentials


class ExchageFactory:
    @staticmethod
    def create_exchange(exchange_id='binance',
                        credential_id='test',
                        enable_rate_limit=True,
                        timeout=3000,
                        sandbox_mode=True):
        exchange = getattr(ccxt, exchange_id)({
            'apiKey': credentials[credential_id]['api_key'],
            'secret': credentials[credential_id]['secret_key'],
            'timeout': timeout,
            'enableRateLimit': enable_rate_limit,
        })
        exchange.set_sandbox_mode(sandbox_mode)
        return exchange
