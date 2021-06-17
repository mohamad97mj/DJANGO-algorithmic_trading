import ccxt.async_support as ccxt
from binance.client import Client as PythonBinanceExchange
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
        ccxt_exchange: ccxt.Exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': enable_rate_limit,
            'verbos': verbose,
        })

        if credential_id:
            ccxt_exchange.apiKey = credentials[credential_id]['api_key']
            ccxt_exchange.secret = credentials[credential_id]['secret_key']
            ccxt_exchange.set_sandbox_mode(enabled=credential_id == 'test')

        # ccxt_exchange.options['createMarketBuyOrderRequiresPrice'] = False
        pb_exchange = None
        if exchange_id == 'binance':
            pb_exchange = PythonBinanceExchange(
                api_key=credentials[credential_id]['api_key'],
                api_secret=credentials[credential_id]['api_key'],
                testnet=credential_id == 'test',
            )

        exchange = Exchange(ccxt_exchange=ccxt_exchange, pb_exchange=pb_exchange)
        self._exchanges.append(exchange)
        return exchange

    async def close_all_exchages(self):
        for exchange in self._exchanges:
            await exchange.close()


ef = ExchageFactory()
