from trader.clients.public_client import PublicClient
from .. import SpotPosition
import numpy as np


class SpotStrategyCenter:

    def __init__(self, exchange_id):
        self.strategy_mapper = {
            'trailing_stoploss': self.set_trailing_stoploss_strategy,
        }
        self._public_client = PublicClient(exchange_id)

    def set_strategy_operations(self, position: SpotPosition):
        return self.strategy_mapper[position.strategy](position=position)

    def set_trailing_stoploss_strategy(self, position: SpotPosition):
        symbol = position.signal.symbol
        # ticker = self._public_client.fetch_ticker(symbol=symbol)
        # print(ticker)
        limit = 1000
        ohlcvs = self._public_client.fetch_ohlcv(symbol=symbol, limit=limit)
        limit_step_ratios = np.arange(0.005, 0.051, 0.005)
        stoploss2limit_ratios = np.arange(0.005, 0.51, 0.005)

        results = []

        trailing_modes = [
            # 'soft',
            'hard',
        ]

        for mode in trailing_modes:
            for r1 in limit_step_ratios:
                for r2 in stoploss2limit_ratios:
                    amount_in_quote = 100
                    closing_price = ohlcvs[0][4]
                    amount = amount_in_quote / closing_price
                    amount_in_quote = 0
                    next_stoploss_price = closing_price * (1 - r1 * r2)
                    next_upper_buy_limit_price = closing_price
                    next_lower_buy_limit_price = closing_price * (1 - r1)

                    for i in range(1, len(ohlcvs)):
                        next_closing_price = ohlcvs[i][4]
                        if next_closing_price > closing_price:
                            if next_closing_price > next_upper_buy_limit_price:
                                if amount_in_quote:
                                    amount = amount_in_quote / next_upper_buy_limit_price
                                    amount_in_quote = 0
                                next_stoploss_price = next_closing_price * (1 - r1 * r2)
                                next_upper_buy_limit_price = next_closing_price
                                next_lower_buy_limit_price = next_closing_price * (1 - r1)

                        else:
                            if amount:
                                if next_closing_price < next_stoploss_price:
                                    amount_in_quote = amount * next_stoploss_price
                                    amount = 0
                            if next_closing_price < next_lower_buy_limit_price:
                                amount = amount_in_quote / next_closing_price
                                amount_in_quote = 0
                                next_stoploss_price = next_closing_price * (1 - r1 * r2)
                                next_upper_buy_limit_price = next_closing_price
                                next_lower_buy_limit_price = next_closing_price * (1 - r1)

                        closing_price = next_closing_price
                    if amount:
                        amount_in_quote = amount * closing_price
                    results.append(
                        {
                            'trailing_mode': mode,
                            'limit_step_ratio': r1,
                            'stoploss2limit_ratio': r2,
                            'final_amount_in_quote': amount_in_quote,
                        }
                    )
                    sorted_results = sorted(results, key=lambda k: k['final_amount_in_quote'], reverse=True)
        print("finished")
