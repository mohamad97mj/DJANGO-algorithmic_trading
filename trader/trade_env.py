from trader.models import Operation
from trader.exchange import ef


class TradeEnv:

    def __init__(self):
        self.bots = []

    def get_not_executed_operations(self):
        self.operations = Operation.objects.filter(is_executed=False)

    def create_bot(self, credential, position):
        pass

    def run_bots(self):
        pass
