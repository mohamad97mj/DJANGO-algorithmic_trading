from typing import Union
from ..models import FuturesOrder, FuturesOperation, FuturesStep, FuturesTarget, FuturesPosition, FuturesStoploss


def create_market_buy_in_quote_operation(symbol,
                                         operation_type,
                                         price,
                                         amount_in_quote,
                                         position: FuturesPosition,
                                         step: FuturesStep = None):
    buy_market_order = FuturesOrder(symbol=symbol,
                                    type='market',
                                    side='buy',
                                    price=price,
                                    amount_in_quote=amount_in_quote)
    buy_market_order.save()
    buy_market_operation = FuturesOperation(
        type=operation_type,
        position=position,
        order=buy_market_order,
        action='create',
        status='in_progress')
    buy_market_operation.save()
    if step:
        step.operation = buy_market_operation
    return buy_market_operation


def create_market_sell_operation(symbol,
                                 operation_type,
                                 price,
                                 amount,
                                 position: FuturesPosition,
                                 stoploss: FuturesStoploss = None):
    sell_market_order = FuturesOrder(symbol=symbol,
                                     type='market',
                                     side='sell',
                                     price=price,
                                     amount=amount)
    sell_market_order.save()
    sell_market_operation = FuturesOperation(
        type=operation_type,
        position=position,
        order=sell_market_order,
        action='create',
        status='in_progress')
    sell_market_operation.save()
    if stoploss:
        stoploss.operation = sell_market_operation
    return sell_market_operation
