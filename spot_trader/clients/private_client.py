from spot_trader.exchange import ef


class PrivateClient:

    def __init__(self, exchange_id, credential_id):
        self._exchange = ef.create_exchange(exchange_id=exchange_id,
                                            credential_id=credential_id)

    def fetch_total_balance(self):
        return self._exchange.fetch_total_balance()

    def fetch_orders(self, symbol='BTC/USDT'):
        return self._exchange.fetch_orders()

    def fetch_order(self, order_id):
        return self._exchange.fetch_order(order_id)

    def fetch_open_orders(self, symbol='BTC/USDT'):
        return self._exchange.fetch_open_orders(symbol=symbol)

    def fetch_closed_orders(self):
        return self._exchange.fetch_closed_orders()

    def fetch_my_trades(self, symbol='BTC/USDT'):
        return self._exchange.fetch_my_trades(symbol=symbol)

    def create_market_buy_order(self, symbol, amount):
        return self._exchange.create_market_buy_order(symbol=symbol, amount=amount)

    def create_market_buy_order_in_quote(self, symbol, amount_in_quote):
        return self._exchange.create_market_buy_order_in_quote(symbol=symbol, amount_in_quote=amount_in_quote)

    def create_market_sell_order(self, symbol, amount):
        return self._exchange.create_market_sell_order(symbol=symbol, amount=amount)

    def create_limit_buy_order(self, symbol, amount, price):
        return self._exchange.create_limit_buy_order(symbol=symbol, amount=amount, price=price)

    def create_limit_sell_order(self, symbol, amount, price):
        return self._exchange.create_limit_sell_order(symbol=symbol, amount=amount, price=price)
