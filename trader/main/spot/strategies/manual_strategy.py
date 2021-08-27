from dataclasses import dataclass
from typing import List
from ..models import SpotPosition, SpotStep, SpotTarget, SpotStoploss, SpotBot
from .utils import create_market_sell_operation, create_market_buy_in_quote_operation
from trader.utils import round_down
from global_utils import my_get_logger, CustomException, JsonSerializable


@dataclass
class StrategyStateData(JsonSerializable):
    symbol: str
    amount_in_quote: float
    amount: float = 0
    none_triggered_steps_share: float = 1.0
    none_triggered_targets_share: float = 1.0
    all_steps_achieved: bool = False
    all_targets_achieved: bool = False
    unrealized_amount_in_quote: float = 0
    profit_in_quote: float = None  # unrealized_amount_in_quote + amount_in_quote - position.size
    profit_rate: float = None  # profit_in_quote / position.size


class ManualStrategyDeveloper:

    @staticmethod
    def validate_position_data(position_data: dict):

        signal_data = position_data.get('signal')
        steps_data = signal_data['steps']
        step_share_set_mode = signal_data.get('step_share_set_mode')
        targets_data = signal_data.get('targets')
        target_share_set_mode = signal_data.get('target_share_set_mode')

        if step_share_set_mode == 'manual':
            total_share = 0
            for step_data in steps_data:
                total_share += round_down(step_data['share'])
                if not step_data['share']:
                    raise CustomException('Step share is required in manual mode')
            if round_down(total_share) != 1:
                raise CustomException('Total shares must be equal to 1')
        if targets_data:
            if target_share_set_mode == 'manual':
                total_share = 0
                for target_data in targets_data:
                    if not target_data['share']:
                        raise CustomException('Target share is required in manual mode')
                    total_share += round_down(target_data.share)
                if round_down(total_share) != 1:
                    raise CustomException('Total shares must be equal to 1')

    @staticmethod
    def get_strategy_symbols(position: SpotPosition):
        return [position.signal.symbol, ]

    @staticmethod
    def init_strategy_state_data(position: SpotPosition):
        signal = position.signal

        steps = signal.related_steps
        targets = signal.related_targets
        if signal.step_share_set_mode == 'manual':
            for step in steps:
                step.amount_in_quote = position.size * step.share
                step.save()

        elif signal.step_share_set_mode == 'auto':
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

        if targets:
            if signal.target_share_set_mode == 'auto':
                auto_target_share = round_down(1 / len(targets))
                for i in range(len(targets) - 1):
                    target = targets[i]
                    target.share = auto_target_share
                    target.save()
                last_target = targets[len(targets) - 1]
                last_target.share = round(1 - (len(targets) - 1) * auto_target_share, 2)
                last_target.save()

        strategy_state_data = StrategyStateData(symbol=signal.symbol,
                                                amount_in_quote=position.size)
        return strategy_state_data

    @staticmethod
    def reload_strategy_state_data(position):
        signal = position.signal
        all_steps_achieved = True
        all_targets_achieved = True
        steps = signal.related_steps
        if steps[0].buy_price == -1:
            steps.append(steps.pop(0))
        none_triggered_steps_share = 1.0
        amount_in_quote = 0
        for step in steps:
            if step.is_triggered:
                none_triggered_steps_share = round(none_triggered_steps_share - step.share, 2)
            else:
                amount_in_quote += step.amount_in_quote
                all_steps_achieved = False

        targets = signal.related_targets
        none_triggered_targets_share = 1.0
        amount = 0

        if targets:
            for target in targets:
                if target.is_triggered:
                    amount_in_quote += target.released_amount_in_quote
                    none_triggered_targets_share = round(none_triggered_targets_share - target.share, 2)
                else:
                    all_targets_achieved = False
                    amount += target.amount
        else:
            all_targets_achieved = False

        strategy_state_data = StrategyStateData(
            symbol=signal.symbol,
            amount_in_quote=amount_in_quote,
            amount=amount,
            none_triggered_steps_share=round_down(none_triggered_steps_share),
            none_triggered_targets_share=round_down(none_triggered_targets_share),
            all_steps_achieved=all_steps_achieved,
            all_targets_achieved=all_targets_achieved,

        )
        return strategy_state_data

    @staticmethod
    def get_operations(position: SpotPosition, strategy_state_data: StrategyStateData, symbol_prices: dict):
        logger = my_get_logger()
        operations = []
        signal = position.signal
        symbol = signal.symbol
        stoploss = signal.stoploss
        price = symbol_prices[symbol]

        strategy_state_data.unrealized_amount_in_quote = strategy_state_data.amount * price
        strategy_state_data.profit_in_quote = \
            round_down(
                strategy_state_data.unrealized_amount_in_quote + strategy_state_data.amount_in_quote - position.size)
        strategy_state_data.profit_rate = round_down((strategy_state_data.profit_in_quote / position.size) * 100)

        if stoploss and not stoploss.is_triggered and price < stoploss.trigger_price:
            stoploss_operation = create_market_sell_operation(
                symbol=symbol,
                operation_type='stoploss_triggered',
                price=price,
                amount=stoploss.amount,
                position=position,
                stoploss=stoploss
            )

            stoploss.is_triggered = True
            stoploss.save()
            bot = position.bot
            bot.is_active = False

            if stoploss.is_trailed:
                status = SpotBot.Status.STOPPED_BY_TRAILING_STOPLOSS.value
            else:
                status = SpotBot.Status.STOPPED_BY_STOPLOSS.value

            bot.status = status
            bot.save()

            logger.info(
                'stoploss_triggered_operation: (symbol: {}, price: {}, amount: {})'.format(
                    symbol,
                    price,
                    stoploss.amount))

            operations.append(stoploss_operation)

        else:
            steps = signal.related_steps
            n = 0
            for step in steps:
                if not step.is_triggered and (price < step.buy_price or step.buy_price == -1):
                    if step.buy_price == -1:
                        step.buy_price = price
                    if n == 0:
                        strategy_state_data.all_steps_achieved = True
                    strategy_state_data.none_triggered_steps_share = \
                        round(strategy_state_data.none_triggered_steps_share - step.share, 2)

                    buy_step_operation = create_market_buy_in_quote_operation(
                        symbol=symbol,
                        operation_type='buy_step',
                        price=price,
                        amount_in_quote=step.amount_in_quote,
                        position=position,
                        step=step,
                    )

                    logger.info(
                        'buy_step_operation: (symbol: {}, price: {}, amount_in_quote: {})'.format(
                            strategy_state_data.symbol,
                            price,
                            step.amount_in_quote))

                    step.is_triggered = True
                    step.save()
                    operations.append(buy_step_operation)
                n += 1

            targets = signal.related_targets
            for i in range(len(targets)):
                target = targets[i]
                if price > target.tp_price and not target.is_triggered:
                    if i == len(targets) - 1:
                        strategy_state_data.all_targets_achieved = True
                        if not position.keep_open:
                            bot = position.bot
                            bot.is_active = False
                            bot.status = SpotBot.Status.STOPPED_AFTER_FULL_TARGET.value
                            bot.save()

                    strategy_state_data.none_triggered_targets_share = \
                        strategy_state_data.none_triggered_targets_share - target.share

                    tp_operation = create_market_sell_operation(
                        symbol=symbol,
                        operation_type='take_profit',
                        price=price,
                        amount=target.amount,
                        position=position,
                        target=target)

                    logger.info(
                        'tp_operation: (symbol: {}, price: {}, amount: {})'.format(symbol,
                                                                                   price,
                                                                                   target.amount))

                    operations.append(tp_operation)
                    target.is_triggered = True
                    if i == 0:
                        new_trigger_price = (steps[len(steps) - 1].buy_price + target.tp_price) / 2
                    else:
                        new_trigger_price = targets[i - 1].tp_price
                    if stoploss:
                        stoploss.trigger_price = new_trigger_price
                    else:
                        stoploss = SpotStoploss(trigger_price=new_trigger_price)
                        signal.stoploss = stoploss
                    stoploss.is_trailed = True
                    stoploss.save()

                target.save()
        return operations

    @staticmethod
    def apply_operation(exchange_order_data, position: SpotPosition, strategy_state_data: StrategyStateData):
        if exchange_order_data.side == 'buy':
            pure_buy_amount = exchange_order_data.amount - exchange_order_data.fee
            strategy_state_data.amount += pure_buy_amount
            strategy_state_data.amount_in_quote -= exchange_order_data.cost
            signal = position.signal
            stoploss = signal.stoploss
            if stoploss:
                stoploss.amount += pure_buy_amount
                stoploss.save()
            related_setup = exchange_order_data.related_setup
            related_setup.amount_in_quote -= exchange_order_data.cost
            related_setup.purchased_amount = pure_buy_amount
            related_setup.save()
            targets = signal.related_targets
            for target in targets:
                target.amount += pure_buy_amount * target.share
                target.save()
        elif exchange_order_data.side == 'sell':
            strategy_state_data.amount -= exchange_order_data.amount
            pure_sell_amount_in_quote = exchange_order_data.cost - exchange_order_data.fee
            strategy_state_data.amount_in_quote += pure_sell_amount_in_quote
            related_setup = exchange_order_data.related_setup
            related_setup.amount -= exchange_order_data.amount
            related_setup.released_amount_in_quote = pure_sell_amount_in_quote
            related_setup.save()

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
    def _edit_none_triggered_steps(position: SpotPosition,
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
            signal.related_steps = new_steps
            signal.save()

        return position

    @staticmethod
    def edit_targets(position, strategy_state_data, new_targets_data, target_share_set_mode='auto'):
        edit_is_required = ManualStrategyDeveloper._has_targets_changed(position,
                                                                        new_targets_data,
                                                                        target_share_set_mode)
        if edit_is_required:
            ManualStrategyDeveloper._edit_none_triggered_targets(position,
                                                                 strategy_state_data,
                                                                 new_targets_data,
                                                                 target_share_set_mode)
            return True
        return False

    @staticmethod
    def _has_targets_changed(position, new_targets_data, target_share_set_mode):
        signal = position.signal
        current_target_share_set_mode = signal.target_share_set_mode
        current_targets = [target for target in signal.related_targets if not target.is_triggered]
        current_targets_data = [
            {
                'tp_price': t.tp_price,
                'share': t.share,
            } for t in current_targets
        ]
        sorted_new_targets_data = sorted(new_targets_data, key=lambda target: target['tp_price'])
        return current_targets_data != sorted_new_targets_data or (
                current_target_share_set_mode != 'semi_auto' and current_target_share_set_mode != target_share_set_mode)

    @staticmethod
    def _edit_none_triggered_targets(position: SpotPosition,
                                     strategy_state_data: StrategyStateData,
                                     new_targets_data: List[dict],
                                     target_share_set_mode):
        signal = position.signal
        targets = signal.related_targets
        if strategy_state_data.all_targets_achieved:
            raise CustomException('Editing targets is not possible because all targets has been triggered!')
        else:
            if target_share_set_mode == 'manual':
                total_share = 0
                for target_data in new_targets_data:
                    if not target_data['share']:
                        raise CustomException('target share is required in manual mode')
                    total_share += round_down(target_data['share'])
                if round_down(total_share) != round_down(strategy_state_data.none_triggered_targets_share):
                    raise CustomException('Total shares must be equal to free share, free share is : {}'.format(
                        strategy_state_data.none_triggered_targets_share))
                if signal.target_share_set_mode == 'auto':
                    if targets[len(targets) - 1].is_triggered:
                        signal.target_share_set_mode = 'semi_auto'
                    else:
                        signal.target_share_set_mode = 'manual'
            elif target_share_set_mode == 'auto':
                auto_target_share = round_down(strategy_state_data.none_triggered_targets_share / len(new_targets_data))
                for i in range(len(new_targets_data) - 1):
                    new_targets_data[i]['share'] = auto_target_share
                new_targets_data[len(new_targets_data) - 1]['share'] = round(
                    strategy_state_data.none_triggered_targets_share - (len(new_targets_data) - 1) * auto_target_share,
                    2)
                if signal.target_share_set_mode == 'manual':
                    if targets[len(targets) - 1].is_triggered:
                        signal.target_share_set_mode = 'semi_auto'
                    else:
                        signal.target_share_set_mode = 'auto'

            for target in targets:
                if not target.is_triggered:
                    target.delete()

            new_targets = []
            for target_data in new_targets_data:
                target = SpotTarget(
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
    def edit_size(position: SpotPosition, strategy_state_data: StrategyStateData, new_size):
        edit_is_required = ManualStrategyDeveloper._has_size_changed(position, new_size)
        signal = position.signal
        steps = signal.related_steps
        if edit_is_required:
            if steps[len(steps) - 1].is_triggered:
                raise CustomException('Editing steps is not possible because one step has been triggered!')

            amount_in_quote = 0
            for step in steps:
                step.amount_in_quote = step.share * new_size
                amount_in_quote += step.amount_in_quote
                step.save()
            strategy_state_data.amount_in_quote = amount_in_quote
            position.size = new_size
            position.save()

            return True
        return False

    @staticmethod
    def _has_size_changed(position, new_size):
        return position.size != new_size

    @staticmethod
    def edit_stoploss(position: SpotPosition, strategy_state_data: StrategyStateData, new_stoploss_data):
        edit_is_required = ManualStrategyDeveloper._has_stoploss_changed(position, new_stoploss_data)
        if edit_is_required:
            signal = position.signal
            stoploss = signal.stoploss
            if stoploss:
                stoploss.trigger_price = new_stoploss_data['trigger_price']
            else:
                stoploss = SpotStoploss(trigger_price=new_stoploss_data['trigger_price'],
                                        amount=strategy_state_data.amount)
                signal.stoploss = stoploss
            stoploss.save()
            signal.save()
            return True
        return False

    @staticmethod
    def _has_stoploss_changed(position: SpotPosition, new_stoploss):
        if position.signal.stoploss:
            return position.signal.stoploss.trigger_price != new_stoploss['trigger_price']
        return True
