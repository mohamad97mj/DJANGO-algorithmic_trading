import ccxt
from ccxt.base.errors import NetworkError
from global_utils import retry_on_timeout
from trader.utils import apply2all_methods, slash2dash
from .sdk_exchange import SdkExchange


@apply2all_methods(retry_on_timeout(timeout_errors=NetworkError))
class Exchange:
    default_params = {
    }

    def __init__(self,
                 exchange_id,
                 sdk_exchange: SdkExchange):

        self._exchange_id = exchange_id
        self._sdk_exchange = sdk_exchange

    def create_market_order(self):
        pass

