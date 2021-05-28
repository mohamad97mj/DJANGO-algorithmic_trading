import ccxt.async_support as ccxt
from trader.auth import credentials
from .exchange import Exchange
from typing import List


class ExchageFactory:

    def __init__(self):
        self._exchanges: List[Exchange] = []

    def create_exchange(self,
                        exchange_id: str,
                        credential_id: str = None,
                        enable_rate_limit: bool = True,
                        verbose: bool = True) -> Exchange:
        third_party_exchange: ccxt.Exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': enable_rate_limit,
            'verbos': verbose,
        })

        if credential_id:
            third_party_exchange.apiKey = credentials[credential_id]['api_key']
            third_party_exchange.secret = credentials[credential_id]['secret_key']

        if credential_id == 'test':
            third_party_exchange.set_sandbox_mode(enabled=True)

        exchange = Exchange(third_party_exchange=third_party_exchange)
        self._exchanges.append(exchange)
        return exchange

    async def close_all_exchages(self):
        for exchange in self._exchanges:
            await exchange.close()


ef = ExchageFactory()
