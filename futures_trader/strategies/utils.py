from typing import Union
from ..models import FuturesOrder, FuturesOperation, FuturesStep, FuturesTarget, FuturesPosition, FuturesStoploss


def create_market_buy_operation(symbol,
                                operation_type,
                                price,
                                margin,
                                leverage,
                                position: FuturesPosition,
                                step: FuturesStep):
    size = int((margin * leverage) / price)
    buy_market_order = FuturesOrder(symbol=symbol,
                                    type='market',
                                    side='buy',
                                    price=price,
                                    leverage=leverage,
                                    size=size)
    buy_market_order.save()
    buy_market_operation = FuturesOperation(
        type=operation_type,
        position=position,
        order=buy_market_order,
        action='create',
        status='in_progress')
    buy_market_operation.save()
    step.size = size
    step.operation = buy_market_operation
    return buy_market_operation


def create_market_sell_operation(symbol,
                                 operation_type,
                                 price,
                                 size,
                                 leverage,
                                 position: FuturesPosition,
                                 stoploss: FuturesStoploss = None):
    sell_market_order = FuturesOrder(symbol=symbol,
                                     type='market',
                                     side='sell',
                                     price=price,
                                     leverage=leverage,
                                     size=size)
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
