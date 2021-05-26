from pprint import pprint
from trader.global_utils import apply2all_methods, log


@apply2all_methods(log)
class PublicClient:
    def __init__(self, exchange):
        self._exchange = exchange
