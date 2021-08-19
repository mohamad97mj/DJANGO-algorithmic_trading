from ..models import SpotOrder, SpotOperation, SpotStep, SpotTarget, SpotPosition


def create_market_buy_in_quote_operation(symbol,
                                         operation_type,
                                         price,
                                         amount_in_quote,
                                         position: SpotPosition,
                                         step: SpotStep = None):
    buy_market_order = SpotOrder(symbol=symbol,
                                 type='market',
                                 side='buy',
                                 price=price,
                                 amount_in_quote=amount_in_quote)
    buy_market_order.save()
    buy_market_operation = SpotOperation(
        type=operation_type,
        position=position,
        order=buy_market_order,
        action='create',
        status='in_progress')
    buy_market_operation.save()
    if step:
        step.operation = buy_market_operation
        step.save()
    return buy_market_operation


def create_market_sell_operation(symbol,
                                 operation_type,
                                 price, amount,
                                 position: SpotPosition,
                                 target: SpotTarget = None):
    sell_market_order = SpotOrder(symbol=symbol,
                                  type='market',
                                  side='sell',
                                  price=price,
                                  amount=amount)
    sell_market_order.save()
    sell_market_operation = SpotOperation(
        type=operation_type,
        position=position,
        order=sell_market_order,
        action='create',
        status='in_progress')
    sell_market_operation.save()
    if target:
        target.operation = sell_market_operation
        target.save()
    return sell_market_operation
