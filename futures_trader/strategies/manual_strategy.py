from dataclasses import dataclass
from typing import List
from ..models import FuturesPosition, FuturesStep, FuturesTarget, FuturesStoploss, FuturesBot
from .utils import create_market_sell_operation, create_market_buy_operation
from global_utils import my_get_logger, CustomException, JsonSerializable, round_down


@dataclass
class StrategyStateData(JsonSerializable):
    symbol: str
    available_margin: float
    size: float = 0
    none_triggered_steps_share: float = 1.0
    all_steps_achieved: bool = False
    all_targets_achieved: bool = False
    unrealized_margin: float = 0
    total_pnl: float = None  # unrealized_margin + available_margin - position.margin
    total_pnl_percentage: float = None  # total_pnl / position.margin


class ManualStrategyDeveloper:

    @staticmethod
    def validate_position_data(position_data: dict):

        signal_data = position_data.get('signal')
        steps_data = signal_data['steps']
        step_share_set_mode = signal_data.get('step_share_set_mode')

        if step_share_set_mode == 'manual':
            total_share = 0
            for step_data in steps_data:
                total_share += round_down(step_data['share'])
                if not step_data['share']:
                    raise CustomException('Step share is required in manual mode')
            if round_down(total_share) != 1:
                raise CustomException('Total shares must be equal to 1')

    @staticmethod
    def get_strategy_symbols(position: FuturesPosition):
        return [position.signal.symbol, ]

    @staticmethod
    def init_strategy_state_data(position: FuturesPosition):
        signal = position.signal

        steps = signal.related_steps
        if signal.step_share_set_mode == 'manual':
            for step in steps:
                step.margin = int(position.margin * step.share)
                step.save()

        elif signal.step_share_set_mode == 'auto':
            auto_step_share = round_down(1 / len(steps))
            for i in range(len(steps) - 1):
                step = steps[i]
                step.share = auto_step_share
                step.margin = int(position.margin * step.share)
                step.save()
            last_step = steps[len(steps) - 1]
            last_step.share = round(1 - (len(steps) - 1) * auto_step_share, 2)
            last_step.margin = position.margin * last_step.share
            last_step.save()

        strategy_state_data = StrategyStateData(symbol=signal.symbol,
                                                available_margin=position.margin)
        return strategy_state_data

    @staticmethod
    def reload_strategy_state_data(position: FuturesPosition):
        signal = position.signal
        all_steps_achieved = True
        steps = signal.related_steps
        if steps[0].buy_price == -1:
            steps.append(steps.pop(0))
        none_triggered_steps_share = 1.0
        available_margin = position.margin
        size = 0
        for step in steps:
            if step.is_triggered:
                none_triggered_steps_share = round(none_triggered_steps_share - step.share, 2)
                size += step.size
                available_margin -= step.cost
            else:
                all_steps_achieved = False

        all_targets_achieved = False
        targets = signal.related_targets

        if targets:
            for target in targets:
                if not target.is_triggered:
                    all_targets_achieved = False
                    break
            else:
                all_targets_achieved = True

        strategy_state_data = StrategyStateData(
            symbol=signal.symbol,
            available_margin=available_margin,
            size=size,
            none_triggered_steps_share=round_down(none_triggered_steps_share),
            all_steps_achieved=all_steps_achieved,
            all_targets_achieved=all_targets_achieved,
        )
        return strategy_state_data

    @staticmethod
    def get_operations(position: FuturesPosition, strategy_state_data: StrategyStateData, symbol_prices: dict):
        logger = my_get_logger()
        operations = []
        bot = position.bot
        signal = position.signal
        symbol = signal.symbol
        stoploss = signal.stoploss
        price = symbol_prices[symbol]

        strategy_state_data.unrealized_margin = strategy_state_data.size * price / position.leverage
        strategy_state_data.total_pnl = \
            round_down(
                strategy_state_data.unrealized_margin + strategy_state_data.available_margin - position.margin)
        strategy_state_data.total_pnl_percentage = round_down((strategy_state_data.total_pnl / position.margin) * 100)

        if bot.status == FuturesBot.Status.RUNNING.value and stoploss \
                and not stoploss.is_triggered and position.size and price < stoploss.trigger_price:
            stoploss_operation = create_market_sell_operation(
                symbol=symbol,
                operation_type='stoploss_triggered',
                price=price,
                size=position.size,
                position=position,
                stoploss=stoploss
            )

            stoploss.is_triggered = True
            stoploss.save()
            bot.is_active = False

            if stoploss.is_trailed:
                status = FuturesBot.Status.STOPPED_BY_TRAILING_STOPLOSS.value
            else:
                status = FuturesBot.Status.STOPPED_BY_STOPLOSS.value

            bot.final_pnl = strategy_state_data.total_pnl
            bot.final_pnl_percentage = strategy_state_data.total_pnl_percentage
            bot.status = status
            bot.save()

            logger.info(
                'stoploss_triggered_operation: (symbol: {}, price: {}, size: {})'.format(
                    symbol,
                    price,
                    position.size))

            operations.append(stoploss_operation)

        else:
            steps = signal.related_steps
            n = 0
            for step in steps:
                if bot.status == FuturesBot.Status.RUNNING.value and not step.is_triggered and (
                        price < step.buy_price or step.buy_price == -1):
                    if step.buy_price == -1:
                        step.buy_price = price
                    if n == 0:
                        strategy_state_data.all_steps_achieved = True
                    strategy_state_data.none_triggered_steps_share = \
                        round(strategy_state_data.none_triggered_steps_share - step.share, 2)

                    buy_step_operation = create_market_buy_operation(
                        symbol=symbol,
                        operation_type='buy_step',
                        price=price,
                        margin=step.margin,
                        position=position,
                        step=step,
                    )

                    logger.info(
                        'buy_step_operation: (symbol: {}, price: {}, size: {})'.format(
                            symbol,
                            price,
                            step.size))

                    step.is_triggered = True
                    step.save()
                    operations.append(buy_step_operation)
                n += 1

            targets = signal.related_targets
            for i in range(len(targets)):
                target = targets[i]
                if bot.status == FuturesBot.Status.RUNNING.value and price > target.tp_price and not target.is_triggered:
                    if i == len(targets) - 1:
                        strategy_state_data.all_targets_achieved = True
                        if not position.keep_open:
                            full_target_operation = create_market_sell_operation(
                                symbol=symbol,
                                operation_type='full_target',
                                price=price,
                                size=position.size,
                                position=position,
                            )

                            logger.info(
                                'full_target_operation: (symbol: {}, price: {}, size: {})'.format(
                                    symbol,
                                    price,
                                    position.size))

                            operations.append(full_target_operation)

                            bot.final_pnl = strategy_state_data.total_pnl
                            bot.final_pnl_percentage = strategy_state_data.total_pnl_percentage
                            bot.is_active = False
                            bot.status = FuturesBot.Status.STOPPED_AFTER_FULL_TARGET.value
                            bot.save()

                    target.is_triggered = True
                    stoploss_is_created = False
                    if i == 0:
                        new_trigger_price = steps[len(steps) - 1].buy_price
                    else:
                        new_trigger_price = targets[i - 1].tp_price
                    if stoploss:
                        stoploss.trigger_price = new_trigger_price
                    else:
                        stoploss = FuturesStoploss(trigger_price=new_trigger_price, amount=strategy_state_data.size)
                        stoploss_is_created = True
                    stoploss.is_trailed = True
                    stoploss.save()
                    if stoploss_is_created:
                        signal.stoploss = stoploss
                        signal.save()
                target.save()
        return operations

    @staticmethod
    def edit_steps(position, strategy_state_data, new_steps_data, step_share_set_mode='auto'):
        edit_is_required = ManualStrategyDeveloper._has_steps_changed(position,
                                                                      new_steps_data,
                                                                      step_share_set_mode)
        if edit_is_required:
            ManualStrategyDeveloper._edit_none_triggered_steps(position,
                                                               strategy_state_data,
                                                               new_steps_data,
                                                               step_share_set_mode)
            return True
        return False

    @staticmethod
    def _has_steps_changed(position, new_steps_data, step_share_set_mode):
        signal = position.signal
        current_step_share_set_mode = signal.step_share_set_mode
        current_steps = [step for step in signal.related_steps if not step.is_triggered]
        current_steps_data = [
            {
                'buy_price': s.buy_price,
                'share': s.share,
            } for s in current_steps
        ]
        sorted_new_steps_data = sorted(new_steps_data, key=lambda step: step['buy_price'])
        return current_steps_data != sorted_new_steps_data or (
                current_step_share_set_mode != 'semi_auto' and current_step_share_set_mode != step_share_set_mode)

    @staticmethod
    def _edit_none_triggered_steps(position: FuturesPosition,
                                   strategy_state_data: StrategyStateData,
                                   new_steps_data: List[dict],
                                   step_share_set_mode):
        signal = position.signal
        steps = signal.related_steps
        targets = signal.related_targets
        if strategy_state_data.all_steps_achieved:
            raise CustomException('Editing steps is not possible because all steps has been triggered!')
        else:
            if step_share_set_mode == 'manual':
                total_share = 0
                for step_data in new_steps_data:
                    if not step_data['share']:
                        raise CustomException('Step share is required in manual mode')
                    total_share += round_down(step_data['share'])
                if round_down(total_share) != round_down(strategy_state_data.none_triggered_steps_share):
                    raise CustomException('Total shares must be equal to free share, free share is : {}'.format(
                        strategy_state_data.none_triggered_steps_share))
                if signal.step_share_set_mode == 'auto':
                    if steps[len(steps) - 1].is_triggered:
                        signal.step_share_set_mode = 'semi_auto'
                    else:
                        signal.step_share_set_mode = 'manual'
            elif step_share_set_mode == 'auto':
                auto_step_share = round_down(strategy_state_data.none_triggered_steps_share / len(new_steps_data))
                for i in range(len(new_steps_data) - 1):
                    new_steps_data[i]['share'] = auto_step_share
                new_steps_data[len(new_steps_data) - 1]['share'] = round(
                    strategy_state_data.none_triggered_steps_share - (len(new_steps_data) - 1) * auto_step_share, 2)
                if signal.step_share_set_mode == 'manual':
                    if targets[len(targets) - 1].is_triggered:
                        signal.step_share_set_mode = 'semi_auto'
                    else:
                        signal.step_share_set_mode = 'auto'

            for step in steps:
                if not step.is_triggered:
                    step.delete()

            new_steps = []
            for step_data in new_steps_data:
                step = FuturesStep(
                    signal=signal,
                    buy_price=step_data['buy_price'],
                    share=step_data['share'],
                    is_triggered=False,
                    amount_in_quote=position.size * step_data['share']
                )
                step.save()
                new_steps.append(step)

            signal.steps.set(new_steps)
            signal.related_steps = new_steps
            signal.save()

        return position

    @staticmethod
    def edit_targets(position, strategy_state_data, new_targets_data):
        edit_is_required = ManualStrategyDeveloper._has_targets_changed(position,
                                                                        new_targets_data)
        if edit_is_required:
            ManualStrategyDeveloper._edit_none_triggered_targets(position,
                                                                 strategy_state_data,
                                                                 new_targets_data)
            return True
        return False

    @staticmethod
    def _has_targets_changed(position, new_targets_data):
        signal = position.signal
        current_targets = [target for target in signal.related_targets if not target.is_triggered]
        current_targets_data = [
            {
                'tp_price': t.tp_price,
            } for t in current_targets
        ]
        sorted_new_targets_data = sorted(new_targets_data, key=lambda target: target['tp_price'])
        return current_targets_data != sorted_new_targets_data

    @staticmethod
    def _edit_none_triggered_targets(position: FuturesPosition,
                                     strategy_state_data: StrategyStateData,
                                     new_targets_data: List[dict]):
        signal = position.signal
        targets = signal.related_targets
        if strategy_state_data.all_targets_achieved:
            raise CustomException('Editing targets is not possible because all targets has been triggered!')
        else:
            for target in targets:
                if not target.is_triggered:
                    target.delete()

            new_targets = []
            for target_data in new_targets_data:
                target = FuturesTarget(
                    signal=signal,
                    tp_price=target_data['tp_price'],
                    is_triggered=False,
                )
                target.save()
                new_targets.append(target)

            signal.targets.set(new_targets)
            signal.related_targets = new_targets
            signal.save()

        return position

    @staticmethod
    def edit_margin(position: FuturesPosition, strategy_state_data: StrategyStateData, new_margin):
        edit_is_required = ManualStrategyDeveloper._has_margin_changed(position, new_margin)
        signal = position.signal
        steps = signal.related_steps
        if edit_is_required:
            if steps[len(steps) - 1].is_triggered:
                raise CustomException('Editing margin is not possible because one step has been triggered!')

            for step in steps:
                step.margin = step.share * new_margin
                step.save()

            strategy_state_data.available_margin = new_margin
            position.margin = new_margin
            position.save()

            return True
        return False

    @staticmethod
    def _has_margin_changed(position, new_margin):
        return position.margin != new_margin

    @staticmethod
    def edit_stoploss(position: FuturesPosition, strategy_state_data: StrategyStateData, new_stoploss_data):
        edit_is_required = ManualStrategyDeveloper._has_stoploss_changed(position, new_stoploss_data)
        if edit_is_required:
            signal = position.signal
            stoploss = signal.stoploss
            if stoploss:
                stoploss.trigger_price = new_stoploss_data['trigger_price']
            else:
                stoploss = FuturesStoploss(trigger_price=new_stoploss_data['trigger_price'],
                                           amount=strategy_state_data.size)
                signal.stoploss = stoploss
            stoploss.save()
            signal.save()
            return True
        return False

    @staticmethod
    def _has_stoploss_changed(position: FuturesPosition, new_stoploss):
        if position.signal.stoploss:
            return position.signal.stoploss.trigger_price != new_stoploss['trigger_price']
        return True
