import ccxt.async_support as ccxt
from trader.auth import credentials
from .exchange import Exchange


class ExchageFactory:
    @staticmethod
    def create_exchange(exchange_id: str = 'binance',
                        credential_id: str = None,
                        enable_rate_limit: bool = True,
                        sandbox_mode: bool = False) -> Exchange:
        third_party_exchange: ccxt.Exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': enable_rate_limit,
        })

        if credential_id:
            third_party_exchange.apiKey = credentials[credential_id]['api_key']
            third_party_exchange.secret = credentials[credential_id]['secret']

        third_party_exchange.set_sandbox_mode(sandbox_mode)
        exchange = Exchange(third_party_exchange=third_party_exchange)
        return exchange
