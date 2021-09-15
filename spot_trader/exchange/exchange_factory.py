from typing import List
import ccxt
from binance.client import Client as PythonBinanceExchange
from global_utils import retry_on_timeout
from spot_trader.utils import obtain_credential
from .exchange import Exchange
from .sdk_exchange import SdkExchange


class ExchangeFactory:

    def __init__(self):
        self._exchanges: List[Exchange] = []

    def create_exchange(self,
                        exchange_id: str,
                        credential_id: str = None,
                        enable_rate_limit: bool = True,
                        verbose: bool = False) -> Exchange:

        api_key = secret = password = is_sandbox = None
        if credential_id:
            api_key, secret, password = obtain_credential(credential_id)
            is_sandbox = credential_id.endswith('test')

        ccxt_exchange: ccxt.Exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': enable_rate_limit,
            'verbose': verbose,
            'apiKey': api_key,
            'secret': secret,
            'password': password
        })
        ccxt_exchange.set_sandbox_mode(enabled=is_sandbox)
        # ccxt_exchange.options['createMarketBuyOrderRequiresPrice'] = False

        python_exchange = None
        if exchange_id in ('binance',):
            python_exchange = self._create_python_exchange(
                exchange_id=exchange_id,
                api_key=api_key,
                secret=secret,
                is_sandbox=is_sandbox
            )

        sdk_exchange = None
        if exchange_id in ('kucoin',):
            sdk_exchange = self._create_sdk_exchange(exchange_id=exchange_id,
                                                     api_key=api_key,
                                                     secret=secret,
                                                     password=password,
                                                     is_sandbox=is_sandbox)

        exchange = Exchange(exchange_id=exchange_id,
                            ccxt_exchange=ccxt_exchange,
                            python_exchange=python_exchange,
                            sdk_exchange=sdk_exchange
                            )
        self._exchanges.append(exchange)
        return exchange

    @retry_on_timeout(attempts=3)
    def _create_python_exchange(self, exchange_id, api_key, secret, is_sandbox):
        exchange = None
        if exchange_id == 'binance':
            exchange = PythonBinanceExchange(
                api_key=api_key,
                api_secret=secret,
                testnet=is_sandbox,
            )

        return exchange

    def _create_sdk_exchange(self, exchange_id, api_key, secret, password, is_sandbox):
        exchange = None
        if exchange_id == 'kucoin':
            return SdkExchange(
                api_key=api_key,
                secret=secret,
                password=password,
                is_sandbox=is_sandbox
            )

        return exchange

    def close_all_exchanges(self):
        for exchange in self._exchanges:
            exchange.close()


ef = ExchangeFactory()
