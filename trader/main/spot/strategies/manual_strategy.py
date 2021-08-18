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

