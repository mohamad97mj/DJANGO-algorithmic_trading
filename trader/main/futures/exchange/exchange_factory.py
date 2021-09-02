from typing import List
from trader.auth import credentials
from global_utils import retry_on_timeout
from .exchange import Exchange
from .sdk_exchange import SdkExchange
from trader.utils import obtain_credential


class ExchangeFactory:

    def __init__(self):
        self._exchanges: List[Exchange] = []

    def create_exchange(self,
                        exchange_id: str,
                        credential_id: str = None,
                        ) -> Exchange:

        api_key = secret = password = is_sandbox = None
        if credential_id:
            api_key, secret, password = obtain_credential(credential_id)
            is_sandbox = credential_id.endswith('test')

        sdk_exchange = None
        if exchange_id in ('kucoin',):
            sdk_exchange = self._create_sdk_exchange(exchange_id=exchange_id,
                                                     api_key=api_key,
                                                     secret=secret,
                                                     password=password,
                                                     is_sandbox=is_sandbox)

        exchange = Exchange(exchange_id=exchange_id,
                            sdk_exchange=sdk_exchange)
        self._exchanges.append(exchange)
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
