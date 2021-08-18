from ..models import SpotPosition, SpotOrder, SpotOperation


def create_buy_in_quote_operation(symbol, type, price, amount_in_quote, position):
    buy_market_order = SpotOrder(symbol=symbol,
                                 type=type,
                                 side='buy',
                                 price=price,
                                 amount_in_quote=amount_in_quote)
    buy_market_order.save()
    buy_market_operation = SpotOperation(
        order=buy_market_order,
        action='create',
        position=position,
        status='in_progress')
    buy_market_operation.save()
    position.save()
    return buy_market_operation


def create_sell_operation(symbol, type, price, amount, position):
    sell_market_order = SpotOrder(symbol=symbol,
                                  type=type,
                                  side='sell',
                                  price=price,
                                  amount=amount)
    sell_market_order.save()
    sell_market_operation = SpotOperation(
        order=sell_market_order,
        action='create',
        position=position,
        status='in_progress')
    sell_market_operation.save()
    position.save()
    return sell_market_operation
