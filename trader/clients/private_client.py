from pprint import pprint
from trader.global_utils import apply2all_methods, log
from trader.exchange.exchange_factory import ef


@apply2all_methods(log)
class PrivateClient:
    def __init__(self, exchange_id, credential_id):
        self._exchange = ef.create_exchange(exchange_id=exchange_id,
                                            credential_id=credential_id)

    async def fetch_total_balance(self):
        return await self._exchange.fetch_total_balance()
