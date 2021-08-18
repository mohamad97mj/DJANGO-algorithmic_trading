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

