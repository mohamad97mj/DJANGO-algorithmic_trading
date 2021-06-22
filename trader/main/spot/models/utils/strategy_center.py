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
        # symbol = position.signal.symbol
        # ticker = self._public_client.fetch_ticker(symbol=symbol)
        # print(ticker)

        markets = self._public_client.get_markets()
        symbols = markets.keys()
        selected_quote = 'USDT'
        selected_symbols = []
        for symbol in symbols:
            splitted_symbol = symbol.split('/')
            base = splitted_symbol[0]
            quote = splitted_symbol[1]
            if quote == selected_quote:
                if base.endswith('UP') or base.endswith('DOWN'):
                    selected_symbols.append(symbol)

        # selected_symbols = ['SUSHIUP/USDT']
        limit = 100

        # limit_step_ratios = np.arange(0.01, 0.05, 0.01)
        limit_step_ratios = [
            # 0.001,
            # 0.005,
            0.01,
            # 0.05,
            # 0.1,
            # 0.2
        ]
        # stoploss2limit_ratios = np.arange(0.01, 0.05, 0.01)
        stoploss2limit_ratios = [
            # 0.001,
            # 0.005,
            # 0.01,
            # 0.05,
            0.1,
            # 0.2
        ]
        fee = 0.001

        results = []

        trailing_modes = [
            # 'soft',
            'hard',
        ]
        for symbol in selected_symbols:

            ohlcvs = self._public_client.fetch_ohlcv(symbol=symbol, limit=limit)

            for mode in trailing_modes:
                for r1 in limit_step_ratios:
                    for r2 in stoploss2limit_ratios:
                        amount_in_quote = 100
                        closing_price = ohlcvs[0][4]
                        amount = (amount_in_quote * (1 - fee)) / closing_price
                        amount_in_quote = 0
                        next_stoploss_price = closing_price * (1 - r1 * r2)
                        next_upper_buy_limit_price = closing_price
                        next_lower_buy_limit_price = closing_price * (1 - r1)
                        number_of_upper_buy_limit_transactions = 0
                        number_of_lower_buy_limit_transactions = 0
                        number_of_stoploss_triggered_transactions = 0

                        for i in range(1, len(ohlcvs)):
                            next_closing_price = ohlcvs[i][4]
                            if next_closing_price > closing_price:
                                if next_closing_price > next_upper_buy_limit_price:
                                    if amount_in_quote:
                                        amount = (amount_in_quote * (1 - fee)) / next_upper_buy_limit_price
                                        amount_in_quote = 0
                                        number_of_upper_buy_limit_transactions += 1
                                    next_stoploss_price = next_closing_price * (1 - r1 * r2)
                                    next_upper_buy_limit_price = next_closing_price
                                    next_lower_buy_limit_price = next_closing_price * (1 - r1)

                            else:
                                if amount:
                                    if next_closing_price < next_stoploss_price:
                                        amount_in_quote = amount * (1 - fee) * next_stoploss_price
                                        amount = 0
                                        number_of_stoploss_triggered_transactions += 1

                                if next_closing_price < next_lower_buy_limit_price:
                                    amount = (amount_in_quote * (1 - fee)) / next_closing_price
                                    amount_in_quote = 0
                                    number_of_lower_buy_limit_transactions += 1
                                    next_stoploss_price = next_closing_price * (1 - r1 * r2)
                                    next_upper_buy_limit_price = next_closing_price
                                    next_lower_buy_limit_price = next_closing_price * (1 - r1)

                            closing_price = next_closing_price
                        total_number_of_transactions = number_of_lower_buy_limit_transactions + number_of_upper_buy_limit_transactions + number_of_stoploss_triggered_transactions
                        if amount:
                            amount_in_quote = amount * closing_price

                        results.append(
                            {
                                'symbol': symbol,
                                'trailing_mode': mode,
                                'limit_step_ratio': r1,
                                'stoploss2limit_ratio': r2,
                                'profit_rate': ((amount_in_quote - 100) / 100) * 100,
                                'total_number_of_transactions': total_number_of_transactions,
                                'number_of_upper_buy_limit_transactions': number_of_upper_buy_limit_transactions,
                                'number_of_lower_buy_limit_transactions': number_of_lower_buy_limit_transactions,
                                'number_of_stoploss_triggered_transactions': number_of_stoploss_triggered_transactions,
                            }
                        )
        sorted_results = sorted(results, key=lambda k: k['profit_rate'], reverse=True)
        print("finished")
