from ..exchange import ef


class PrivateClient:

    def __init__(self, exchange_id, credential_id):
        self._exchange = ef.create_exchange(exchange_id=exchange_id,
                                            credential_id=credential_id)

    def get_account_overview(self, currency):
        return self._exchange.get_account_overview(currency=currency)

    def get_order(self, order_id):
        return self._exchange.get_order(order_id=order_id)

    def get_orders(self, symbol):
        return self._exchange.get_orders(symbol)

    def create_limit_order(self, symbol, leverage, side, size, price, multiplier):
        return self._exchange.create_limit_order(symbol=symbol,
                                                 leverage=leverage,
                                                 side=side,
                                                 size=size,
                                                 price=price,
                                                 multiplier=multiplier)

    def create_market_order(self, symbol, leverage, side, size, multiplier):
        return self._exchange.create_market_order(symbol=symbol,
                                                  leverage=leverage,
                                                  side=side,
                                                  size=size,
                                                  multiplier=multiplier)

    def create_stop_market_order(self, symbol, leverage, side, size, multiplier, stop, stop_price):
        return self._exchange.create_stop_market_order(symbol=symbol,
                                                       leverage=leverage,
                                                       side=side,
                                                       size=size,
                                                       multiplier=multiplier,
                                                       stop=stop,
                                                       stop_price=stop_price)

    def create_market_buy_order_in_cost(self, symbol, leverage, cost, price, multiplier):
        return self._exchange.create_market_buy_order_in_cost(symbol=symbol,
                                                              leverage=leverage,
                                                              cost=cost,
                                                              price=price,
                                                              multiplier=multiplier)

    def create_market_sell_order_in_cost(self, symbol, leverage, cost, price, multiplier):
        return self._exchange.create_market_sell_order_in_cost(symbol=symbol,
                                                               leverage=leverage,
                                                               cost=cost,
                                                               price=price,
                                                               multiplier=multiplier)

    def cancel_all_limit_orders(self, symbol):
        return self._exchange.cancel_all_limit_orders(symbol)

    def cancel_all_stop_orders(self, symbol):
        return self._exchange.cancel_all_stop_orders(symbol)

    def get_all_positions(self):
        return self._exchange.get_all_positions()

    def get_position(self, symbol):
        return self._exchange.get_position(symbol=symbol)

    def close_position(self, symbol):
        return self._exchange.close_position(symbol=symbol)
