from ..exchange import ef


class PrivateClient:

    def __init__(self, exchange_id, credential_id):
        self._exchange = ef.create_exchange(exchange_id=exchange_id,
                                            credential_id=credential_id)

    def get_order(self, order_id):
        return self._exchange.get_order(order_id=order_id)

    def create_market_buy_order(self, symbol, leverage, size):
        return self._exchange.create_market_buy_order(symbol=symbol, leverage=leverage, size=size)

    def create_market_sell_order(self, symbol, leverage, size):
        return self._exchange.create_market_sell_order(symbol=symbol, leverage=leverage, size=size)

    def create_market_buy_order_in_cost(self, symbol, leverage, cost, price):
        return self._exchange.create_market_buy_order_in_cost(symbol=symbol, leverage=leverage, cost=cost, price=price)

    def create_market_sell_order_in_cost(self, symbol, leverage, cost, price):
        return self._exchange.create_market_sell_order_in_cost(symbol=symbol, leverage=leverage, cost=cost, price=price)

    def get_all_positions(self):
        return self._exchange.get_all_positions()

    def get_position(self, symbol):
        return self._exchange.get_position(symbol=symbol)
