from trader.client import client
from pprint import pprint
from trader.global_utils import apply2all_methods, log
from binance import enums


@apply2all_methods(log)
class SpotTraderBot:
    def __init__(self):
        self._client = client

    def get_dayli_account_snapshot(self):
        info = client.get_account_snapshot(type='SPOT')
        pprint(info)
        return info

    def get_account_info(self):
        info = client.get_account()
        pprint(info)
        return info

    def get_asset_balance(self, asset='BTC'):
        balance = client.get_asset_balance(asset=asset)
        pprint(balance)
        return balance

    def get_asset_details(self):
        details = client.get_asset_details()
        pprint(details)
        return details

    def get_trade_fees(self):
        fees = client.get_trade_fee()
        pprint(fees)
        return fees

    def place_buy_limit_order(self, quantity, price, symbol='BTCUSDT'):
        order = client.order_limit_buy(
            quantity=quantity,
            price=price,
            symbol=symbol,
        )

        pprint(order)
        return order

    def place_sell_limit_order(self, quantity, price, symbol='BTCUSDT'):
        order = client.order_limit_sell(
            quantity=quantity,
            price=price,
            symbol=symbol,
        )

        print(order)
        return order

    def place_buy_market_order(self, quantity, symbol='BTCUSDT'):
        order = client.order_market_buy(
            quantity=quantity,
            symbol=symbol,
        )
        pprint(order)
        return order

    def place_sell_market_order(self, quantity, symbol='BTCUSDT'):
        order = client.order_market_sell(
            quantity=quantity,
            symbol=symbol,
        )
        pprint(order)
        return order

    def check_order_status(self, order_id, symbol='BTCUSDT'):
        order = client.get_order(
            orderId=order_id,
            symbol=symbol,
        )
        pprint(order)
        return order

    def cancel_order(self, order_id, symbol='BTCUSDT'):
        result = client.cancel_order(
            orderId=order_id,
            symbol=symbol,
        )
        pprint(result)
        return result

    def get_symbol_all_orders(self, symbol='BTCUSDT', limit=10):
        orders = client.get_all_orders(symbol=symbol, limit=limit)
        pprint(orders)
        return orders

    def get_symbol_all_open_orders(self, symbol='BTCUSDT'):
        orders = client.get_open_orders(symbol=symbol)
        pprint(orders)
        return orders

    def get_symbol_all_trades(self, symbol='BTCUSDT'):
        trades = client.get_my_trades(symbol=symbol)
        pprint(trades)
        return trades
