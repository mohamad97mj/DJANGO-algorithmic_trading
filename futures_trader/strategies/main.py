from dataclasses import dataclass
from typing import List
from ..models import FuturesPosition, FuturesStep, FuturesTarget, FuturesStoploss, FuturesBot
from .utils import create_market_operation, create_market_operation_in_cost
from global_utils import my_get_logger, CustomException, JsonSerializable, round_down
from futures_trader.utils.app_vars import is_test


@dataclass
class StrategyStateData(JsonSerializable):
    symbol: str
    available_margin: float
    none_triggered_steps_share: float = 1.0
    none_triggered_targets_share: float = 1.0
    all_steps_achieved: bool = False
    all_targets_achieved: bool = False
    unrealized_value: float = 0


class ManualStrategyDeveloper:

    @staticmethod
    def validate_position_data(position_data: dict):

        signal_data = position_data.get('signal')
        steps_data = signal_data['steps']
        setup_mode = signal_data.get('setup_mode')

        if setup_mode == 'manual':
            total_share = 0
            for step_data in steps_data:
                step_share = step_data.get('share')
                if not step_share:
                    raise CustomException('Step share is required in manual mode')
                total_share += round_down(step_share)
            if round_down(total_share) != 1:
                raise CustomException('Total shares must be equal to 1')

    @staticmethod
    def get_strategy_symbols(position: FuturesPosition):
        return [position.signal.symbol, ]

    @staticmethod
    def init_strategy_state_data(position: FuturesPosition):
        signal = position.signal
        strategy_state_data = StrategyStateData(symbol=signal.symbol,
                                                available_margin=position.margin)
        return strategy_state_data

    @staticmethod
    def reload_setup(position: FuturesPosition):
        signal = position.signal
        all_steps_achieved = True
        steps = signal.related_steps
        none_triggered_steps_share = 1.0
        available_margin = position.margin
        for step in steps:
            if step.is_triggered:
                none_triggered_steps_share = round(none_triggered_steps_share - step.share, 2)
                available_margin -= step.cost
            else:
                all_steps_achieved = False

        all_targets_achieved = True
        targets = signal.related_targets
        none_triggered_targets_share = 1.0
        if targets:
            for target in targets:
                if target.is_triggered:
                    none_triggered_targets_share = round(none_triggered_targets_share - target.share, 2)
                else:
                    all_targets_achieved = False
        else:
            all_targets_achieved = False

        strategy_state_data = StrategyStateData(
            symbol=signal.symbol,
            available_margin=available_margin,
            none_triggered_steps_share=round_down(none_triggered_steps_share),
            none_triggered_targets_share=round_down(none_triggered_targets_share),
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

        if position.is_triggered and bot.status == FuturesBot.Status.RUNNING.value and stoploss \
                and not stoploss.is_triggered and position.holding_size and \
                ((signal.side == 'buy' and price < stoploss.trigger_price) or
                 (signal.side == 'sell' and price > stoploss.trigger_price)):

            bot.close_position(test=is_test)

            stoploss.is_triggered = True
            stoploss.save()
            bot.is_active = False

            if stoploss.is_trailed:
                status = FuturesBot.Status.STOPPED_BY_TRAILING_STOPLOSS.value
            else:
                status = FuturesBot.Status.STOPPED_BY_STOPLOSS.value

            bot.status = status

            logger.info(
                'stoploss_triggered: (symbol: {}, price: {}, size: {})'.format(
                    symbol,
                    stoploss.trigger_price,
                    position.holding_size))

        else:
            steps = signal.related_steps
            for i in range(len(steps)):
                step = steps[i]
                if bot.status == FuturesBot.Status.RUNNING.value and not step.is_triggered and (
                        (signal.side == 'buy' and price < step.entry_price) or
                        (signal.side == 'sell' and price > step.entry_price) or
                        step.is_market):

                    if i == 0:
                        position.is_triggered = True
                        position.save()
                    elif i == len(steps) - 1:
                        strategy_state_data.all_steps_achieved = True

                    strategy_state_data.none_triggered_steps_share = \
                        round(strategy_state_data.none_triggered_steps_share - step.share, 2)

                    step_operation = create_market_operation_in_cost(
                        symbol=symbol,
                        operation_type='step',
                        side=signal.side,
                        price=price,
                        margin=step.margin,
                        leverage=signal.leverage,
                        position=position,
                    )

                    logger.info(
                        'step_operation: (symbol: {}, price: {}, margin: {})'.format(
                            symbol,
                            step.entry_price,
                            step.margin))

                    step.operation = step_operation
                    step.is_triggered = True
                    step.save()
                    operations.append(step_operation)
                i += 1

            if position.is_triggered:
                targets = signal.related_targets
                for j in range(len(targets)):
                    target = targets[j]
                    if bot.status == FuturesBot.Status.RUNNING.value and not target.is_triggered and \
                            ((signal.side == 'buy' and price > target.tp_price) or
                             (signal.side == 'sell' and price < target.tp_price)):
                        target.is_triggered = True

                        strategy_state_data.none_triggered_targets_share = \
                            round(strategy_state_data.none_triggered_targets_share - target.share, 2)

                        if not j == (len(targets) - 1):
                            logger.info(
                                'take_profit: (symbol: {}, tp_price: {}, size: {})'.format(
                                    symbol,
                                    target.tp_price,
                                    target.holding_size))

                            tp_operation = create_market_operation(
                                symbol=symbol,
                                operation_type='take_profit',
                                side='sell' if signal.side == 'buy' else 'buy',
                                size=target.holding_size,
                                price=price,
                                leverage=signal.leverage,
                                position=position,
                            )

                            operations.append(tp_operation)
                            target.operation = tp_operation

                            if j == 1 or (j == 0 and signal.leverage > 10):
                                new_trigger_price = steps[0].entry_price
                                stoploss_is_created = False
                                if stoploss:
                                    stoploss.trigger_price = new_trigger_price
                                else:
                                    stoploss = FuturesStoploss(trigger_price=new_trigger_price)
                                    stoploss_is_created = True
                                stoploss.is_trailed = True
                                stoploss.save()
                                if stoploss_is_created:
                                    signal.stoploss = stoploss
                                    signal.save()

                        else:
                            strategy_state_data.all_targets_achieved = True
                            if not position.keep_open:
                                logger.info(
                                    'take_profit: (symbol: {}, tp_price: {}, size: {})'.format(
                                        symbol,
                                        target.tp_price,
                                        target.holding_size))
                                target.holding_size = 0
                                value = position.holding_size * price
                                position.released_margin += value
                                position.holding_size = 0
                                position.save()
                                bot.is_active = False
                                bot.status = FuturesBot.Status.STOPPED_AFTER_FULL_TARGET.value
                                bot.close_position(is_test)
                                bot.save()
                            logger.info('position_full_target')

                        target.save()

        strategy_state_data.unrealized_value = position.holding_size * price
        sign = 1 if signal.side == 'buy' else -1
        bot.total_pnl = round_down(
            sign * ((position.released_margin + strategy_state_data.unrealized_value) - position.purchased_value))
        bot.total_pnl_percentage = round_down((bot.total_pnl / position.margin) * 100)
        bot.save()

        return operations

    def get_operation(self):
        pass

    @staticmethod
    def edit_steps(position, strategy_state_data, new_steps_data, setup_mode='auto'):
        edit_is_required = ManualStrategyDeveloper._has_steps_changed(position,
                                                                      new_steps_data,
                                                                      setup_mode)
        if edit_is_required:
            ManualStrategyDeveloper._edit_none_triggered_steps(position,
                                                               strategy_state_data,
                                                               new_steps_data,
                                                               setup_mode)
            return True
        return False

    @staticmethod
    def _has_steps_changed(position, new_steps_data, setup_mode):
        signal = position.signal
        current_setup_mode = signal.setup_mode
        current_steps = [step for step in signal.related_steps if not step.is_triggered]
        current_steps_data = [
            {
                'entry_price': s.entry_price,
                'share': s.share,
            } for s in current_steps
        ]
        reverse = signal.side == 'buy'
        sorted_new_steps_data = sorted(new_steps_data, reverse=reverse, key=lambda step: step['entry_price'])
        return current_steps_data != sorted_new_steps_data or (
                current_setup_mode != 'semi_auto' and current_setup_mode != setup_mode)

    @staticmethod
    def _edit_none_triggered_steps(position: FuturesPosition,
                                   strategy_state_data: StrategyStateData,
                                   new_steps_data: List[dict],
                                   setup_mode):
        signal = position.signal
        steps = signal.related_steps
        if strategy_state_data.all_steps_achieved:
            raise CustomException('Editing steps is not possible because all steps has been triggered!')
        else:
            if setup_mode == 'manual':
                total_share = 0
                for step_data in new_steps_data:
                    if not step_data['share']:
                        raise CustomException('Step share is required in manual mode')
                    total_share += round_down(step_data['share'])
                if round_down(total_share) != round_down(strategy_state_data.none_triggered_steps_share):
                    raise CustomException('Total shares must be equal to free share, free share is : {}'.format(
                        strategy_state_data.none_triggered_steps_share))
                if signal.setup_mode == 'auto':
                    if steps[0].is_triggered:
                        signal.setup_mode = 'semi_auto'
                    else:
                        signal.setup_mode = 'manual'
            elif setup_mode == 'auto':
                auto_step_share = round_down(strategy_state_data.none_triggered_steps_share / len(new_steps_data))
                for i in range(len(new_steps_data) - 1):
                    new_steps_data[i]['share'] = auto_step_share
                new_steps_data[len(new_steps_data) - 1]['share'] = round(
                    strategy_state_data.none_triggered_steps_share - (len(new_steps_data) - 1) * auto_step_share, 2)
                if signal.setup_mode == 'manual':
                    if steps[0].is_triggered:
                        signal.setup_mode = 'semi_auto'
                    else:
                        signal.setup_mode = 'auto'

            for step in steps:
                if not step.is_triggered:
                    step.delete()

            new_steps = []
            for step_data in new_steps_data:
                step = FuturesStep(
                    signal=signal,
                    entry_price=step_data['entry_price'],
                    share=step_data['share'],
                    is_triggered=False,
                    amount_in_quote=position.holding_size * step_data['share']
                )
                step.save()
                new_steps.append(step)

            signal.steps.set(new_steps)
            signal.related_steps = new_steps
            signal.save()

        return position

    @staticmethod
    def edit_targets(position, strategy_state_data, new_targets_data, setup_mode):
        edit_is_required = ManualStrategyDeveloper._has_targets_changed(position,
                                                                        new_targets_data)
        if edit_is_required:
            ManualStrategyDeveloper._edit_none_triggered_targets(position,
                                                                 strategy_state_data,
                                                                 new_targets_data,
                                                                 setup_mode,
                                                                 )
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
        reverse = signal.side == 'sell'
        sorted_new_targets_data = sorted(new_targets_data, reverse=reverse, key=lambda target: target['tp_price'])
        return current_targets_data != sorted_new_targets_data

    @staticmethod
    def _edit_none_triggered_targets(position: FuturesPosition,
                                     strategy_state_data: StrategyStateData,
                                     new_targets_data: List[dict],
                                     setup_mode):
        signal = position.signal
        targets = signal.related_targets
        if strategy_state_data.all_targets_achieved:
            raise CustomException('Editing targets is not possible because all targets has been triggered!')
        else:
            for target in targets:
                if not target.is_triggered:
                    target.delete()

            if setup_mode == 'manual':
                total_share = 0
                for target_data in new_targets_data:
                    if not target_data['share']:
                        raise CustomException('Target share is required in manual mode')
                    total_share += round_down(target_data['share'])
                if round_down(total_share) != round_down(strategy_state_data.none_triggered_targets_share):
                    raise CustomException('Total shares must be equal to free share, free share is : {}'.format(
                        strategy_state_data.none_triggered_targets_share))
                if signal.setup_mode == 'auto':
                    if targets[0].is_triggered:
                        signal.setup_mode = 'semi_auto'
                    else:
                        signal.setup_mode = 'manual'
            elif setup_mode == 'auto':
                auto_target_share = round_down(strategy_state_data.none_triggered_targets_share / len(new_targets_data))
                for i in range(len(new_targets_data) - 1):
                    new_targets_data[i]['share'] = auto_target_share
                new_targets_data[len(new_targets_data) - 1]['share'] = round(
                    strategy_state_data.none_triggered_targets_share - (len(new_targets_data) - 1) * auto_target_share,
                    2)
                if signal.setup_mode == 'manual':
                    if targets[0].is_triggered:
                        signal.setup_mode = 'semi_auto'
                    else:
                        signal.setup_mode = 'auto'

            new_targets = []
            for target_data in new_targets_data:
                target = FuturesTarget(
                    signal=signal,
                    tp_price=target_data['tp_price'],
                    share=target_data['share'],
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
            if steps[0].is_triggered:
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
                stoploss = FuturesStoploss(trigger_price=new_stoploss_data['trigger_price'])
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
