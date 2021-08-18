import json
from dataclasses import dataclass
from typing import List
from ..models import SpotPosition, SpotStep
from .utils import create_sell_operation, create_buy_in_quote_operation
from trader.utils import round_down
from global_utils import my_get_logger, CustomException, JsonSerializable


@dataclass
class StepData(JsonSerializable):
    buy_price: float
    share: float
    amount_in_quote: float
    is_triggered: bool = False
    purchased_amount: float = None


@dataclass
class TargetData(JsonSerializable):
    tp_price: float
    share: float
    amount: float = 0
    is_triggered: bool = False
    unrealized_amount_in_quote: float = None
    released_amount_in_quote: float = None


@dataclass
class StrategyStateData(JsonSerializable):
    symbol: str
    steps_data: List[StepData]
    targets_data: List[TargetData]
    stoploss: float
    amount_in_quote: float
    amount: float = 0
    free_share: float = 1
    all_steps_achieved: bool = False
    all_targets_achieved: bool = False
    total_unrealized_pnl: float = 0


class ManualStrategyDeveloper:

    @staticmethod
    def init_strategy_state_data(position: SpotPosition):
        signal = position.signal

        steps = signal.steps.all()

        if signal.step_share_set_mode == 'auto':
            auto_step_share = round_down(1 / len(steps))
            for i in range(len(steps) - 1):
                step = steps[i]
                step.share = auto_step_share
                step.amount_in_quote = position.size * step.share
                step.save()
            last_step = steps[len(steps) - 1]
            last_step.share = round(1 - (len(steps) - 1) * auto_step_share, 2)
            last_step.amount_in_quote = position.size * last_step.share
            last_step.save()

        targets = signal.targets.all()

        if signal.target_share_set_mode == 'auto':
            auto_target_share = round_down(1 / len(targets))
            for i in range(len(targets) - 1):
                target = targets[i]
                target.share = auto_target_share
                target.save()
            last_target = targets[len(targets) - 1]
            last_target.share = round(1 - (len(targets) - 1) * auto_target_share, 2)
            last_target.save()

        # TODO check if it is sorted already
        sorted_steps = sorted(steps, key=lambda s: s.buy_price)
        sorted_targets = sorted(targets, key=lambda t: t.tp_price)

        steps_data = [
            StepData(buy_price=s.buy_price, share=s.share, amount_in_quote=s.share * position.size)
            for s in sorted_steps
        ]
        targets_data = [TargetData(tp_price=t.tp_price, share=t.share) for t in sorted_targets]

        strategy_state_data = StrategyStateData(symbol=signal.symbol,
                                                steps_data=steps_data,
                                                targets_data=targets_data,
                                                stoploss=signal.stoploss,
                                                amount_in_quote=position.size)
        return strategy_state_data

    @staticmethod
    def reload_strategy_state_data(position):
        signal = position.signal
        all_steps_achieved = True
        all_targets_achieved = True
        steps = signal.steps.all()
        sorted_steps = sorted(steps, key=lambda s: s.buy_price)
        steps_data = []
        free_share = 0
        amount_in_quote = 0
        for step in sorted_steps:
            if not step.is_triggered:
                free_share += step.share
                amount_in_quote += step.amount_in_quote
                all_steps_achieved = False
            steps_data.append(
                StepData(buy_price=step.buy_price,
                         share=step.share,
                         amount_in_quote=step.amount_in_quote,
                         is_triggered=step.is_triggered))

        targets = signal.targets.all()
        sorted_targets = sorted(targets, key=lambda t: t.tp_price)
        targets_data = []
        amount = 0
        for target in sorted_targets:
            if not target.is_triggered:
                all_targets_achieved = False
                amount += target.amount
            targets_data.append(
                TargetData(tp_price=target.tp_price,
                           share=target.share,
                           amount=target.amount,
                           is_triggered=target.is_triggered))

        strategy_state_data = StrategyStateData(
            symbol=signal.symbol,
            steps_data=steps_data,
            targets_data=targets_data,
            stoploss=signal.stoploss,
            amount_in_quote=amount_in_quote,
            amount=amount,
            free_share=free_share,
            all_steps_achieved=all_steps_achieved,
            all_targets_achieved=all_targets_achieved,
        )
        return strategy_state_data

    @staticmethod
    def get_strategy_symbols(position: SpotPosition):
        return [position.signal.symbol, ]

    @staticmethod
    def get_operations(position: SpotPosition, strategy_state_data: StrategyStateData, symbol_prices: dict):
        logger = my_get_logger()
        operations = []
        price = symbol_prices[strategy_state_data.symbol]

        if price < strategy_state_data.stoploss:
            stoploss_operation = create_sell_operation(
                symbol=strategy_state_data.symbol,
                type='market',
                price=price,
                amount=strategy_state_data.amount,
                position=position)

            logger.info(
                'stoploss_triggered_operation: (symbol: {}, price: {}, amount: {})'.format(
                    strategy_state_data.symbol,
                    price,
                    strategy_state_data.amount))

            operations.append(stoploss_operation)

        else:
            n = 0
            for step_data in strategy_state_data.steps_data:
                if not step_data.is_triggered and (price < step_data.buy_price or step_data.buy_price == -1):
                    if n == 0:
                        strategy_state_data.all_steps_achieved = True
                    strategy_state_data.free_share -= step_data.share
                    buy_step_operation = create_buy_in_quote_operation(
                        symbol=strategy_state_data.symbol,
                        type='market',
                        price=price,
                        amount_in_quote=step_data.amount_in_quote,
                        position=position)

                    logger.info(
                        'buy_step_operation: (symbol: {}, price: {}, amount_in_quote: {})'.format(
                            strategy_state_data.symbol,
                            price,
                            step_data.amount_in_quote))

                    step_data.is_triggered = True
                    operations.append(buy_step_operation)
                n += 1

            for i in range(len(strategy_state_data.targets_data)):
                target_data = strategy_state_data.targets_data[i]
                if not target_data.is_triggered and price > target_data.tp_price:
                    if i == len(strategy_state_data.targets_data) - 1:
                        strategy_state_data.all_targets_achieved = True
                    tp_operation = create_sell_operation(
                        symbol=strategy_state_data.symbol,
                        type='market',
                        price=price,
                        amount=target_data.amount,
                        position=position)

                    logger.info(
                        'tp_operation: (symbol: {}, price: {}, amount: {})'.format(
                            strategy_state_data.symbol,
                            price,
                            target_data.amount))

                    operations.append(tp_operation)
                    target_data.is_triggered = True
                    if i == 0:
                        strategy_state_data.stoploss = \
                            strategy_state_data.steps_data[len(strategy_state_data.steps_data) - 1].buy_price
                    else:
                        strategy_state_data.stoploss = strategy_state_data.targets_data[i - 1].tp_price

        return operations

    @staticmethod
    def update_strategy_state_data(exchange_order, strategy_state_data):
        if exchange_order['side'] == 'buy':
            pure_buy_amount = exchange_order['amount'] - exchange_order['fee']['cost']
            strategy_state_data.amount += pure_buy_amount
            for target_data in strategy_state_data.targets_data:
                target_data.amount += pure_buy_amount * target_data.share
        elif exchange_order['side'] == 'sell':
            strategy_state_data.amount -= exchange_order['amount']

    @staticmethod
    def validate_position_data(position_data: dict):

        signal_data = position_data.get('signal')
        steps_data = signal_data['steps']
        step_share_set_mode = signal_data['step_share_set_mode']
        targets_data = signal_data['targets']
        target_share_set_mode = signal_data['target_share_set_mode']

        if step_share_set_mode == 'manual':
            total_share = 0
            for step_data in steps_data:
                total_share += round_down(step_data['share'])
                if not step_data['share']:
                    raise CustomException('Step share is required in manual mode')
            if total_share != 1:
                raise CustomException('Total shares must be equal to 1')

        if target_share_set_mode == 'manual':
            total_share = 0
            for target_data in targets_data:
                if not target_data['share']:
                    raise CustomException('Target share is required in manual mode')
                total_share += round_down(target_data.share)
            if total_share != 1:
                raise CustomException('Total shares must be equal to 1')

    @staticmethod
    def edit_none_triggered_steps(position: SpotPosition,
                                  strategy_state_data: StrategyStateData,
                                  new_steps_data: List[dict],
                                  step_share_set_mode='auto'):
        signal = position.signal
        if strategy_state_data.all_steps_achieved:
            raise CustomException('Editing steps is not possible because all steps are triggered!')
        else:
            if step_share_set_mode == 'manual':
                total_share = 0
                for step_data in new_steps_data:
                    if not step_data['share']:
                        raise CustomException('Step share is required in manual mode')
                    total_share += round_down(step_data['share'])
                if total_share != strategy_state_data.free_share:
                    raise CustomException('Total shares must be equal to free share, free share is : {}'.format(
                        strategy_state_data.free_share))
                if signal.step_share_set_mode == 'auto':
                    signal.step_share_set_mode = 'semi_auto'

            elif step_share_set_mode == 'auto':
                auto_step_share = round_down(strategy_state_data.free_share / len(new_steps_data))
                for i in range(len(new_steps_data) - 1):
                    new_steps_data[i]['share'] = auto_step_share
                new_steps_data[len(new_steps_data) - 1]['share'] = round(
                    1 - (len(new_steps_data) - 1) * auto_step_share, 2)
                if signal.step_share_set_mode == 'manual':
                    signal.step_share_set_mode = 'semi_auto'

            signal.steps.filter(is_triggered=False).delete()

            new_steps = []
            for step_data in new_steps_data:
                step = SpotStep(
                    signal=signal,
                    buy_price=step_data['buy_price'],
                    share=step_data['share'],
                    is_triggered=False,
                    amount_in_quote=position.size * step_data['share']
                )
                step.save()
                new_steps.append(step)

            signal.steps.set(new_steps)
            signal.save()
            position.save()

        return position

    @staticmethod
    def edit_step():
        return 'edit_step'

    @staticmethod
    def add_target():
        return 'add_target'

    @staticmethod
    def edit_target():
        return 'edit_target'
