from ..models import FuturesOrder, FuturesOperation, FuturesStep, FuturesPosition, FuturesStoploss


def create_market_operation_in_cost(symbol,
                                    operation_type,
                                    side,
                                    price,
                                    margin,
                                    position: FuturesPosition,
                                    step: FuturesStep):
    size = (margin * position.leverage) / price
    market_order = FuturesOrder(symbol=symbol,
                                type='market',
                                side=side,
                                price=price,
                                leverage=position.leverage,
                                size=size,
                                status='created',
                                )
    market_order.save()
    market_operation = FuturesOperation(
        type=operation_type,
        position=position,
        order=market_order,
        action='create',
        status='in_progress')
    market_operation.save()
    step.purchased_size = int(size)
    step.operation = market_operation
    return market_operation


def create_market_operation(symbol,
                            operation_type,
                            side,
                            price,
                            size,
                            position: FuturesPosition,
                            stoploss: FuturesStoploss = None):
    market_order = FuturesOrder(symbol=symbol,
                                type='market',
                                side=side,
                                price=price,
                                leverage=position.leverage,
                                size=size,
                                status='created')
    market_order.save()
    market_operation = FuturesOperation(
        type=operation_type,
        position=position,
        order=market_order,
        action='create',
        status='in_progress')
    market_operation.save()
    if stoploss:
        stoploss.operation = market_operation
    return market_operation
