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

