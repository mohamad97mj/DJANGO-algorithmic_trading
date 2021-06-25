from trader.clients.public_client import PublicClient
from .. import SpotPosition
from trader.global_utils import truncate
import numpy as np


class SpotStrategyCenter:

    def __init__(self, exchange_id):
        self._trailing_stoploss_strategy_developer = TrailingStoplossStrategyDeveolper(exchange_id)

        self._strategy_mapper = {
            'trailing_stoploss': self._trailing_stoploss_strategy_developer.set_operations,
        }
        self._public_client = PublicClient(exchange_id)

    def set_strategy_operations(self, strategy: str, position: SpotPosition):
        return self._strategy_mapper[strategy](position=position)


class TrailingStoplossStrategyDeveolper:
    def __init__(self, exchange_id):
        self._public_client = PublicClient(exchange_id)
        self._init_optimum_parameters()

    def set_operations(self, position: SpotPosition):
        pass

    def _init_optimum_parameters(self):
        markets = self._public_client.get_markets()
        symbols = markets.keys()
        selected_quote = 'USDT'
        leveraged_symbols = []
        for symbol in symbols:
            splitted_symbol = symbol.split('/')
            base = splitted_symbol[0]
            quote = splitted_symbol[1]
            if quote == selected_quote:
                if base.endswith('UP') or base.endswith('DOWN'):
                    leveraged_symbols.append(symbol)
        tickers = self._public_client.fetch_tickers(symbols=leveraged_symbols)

        selected_symbols = []
        for symbol in leveraged_symbols:
            sample_price = tickers[symbol]['bid']
            integer_part_length = len(str(int(sample_price))) if int(sample_price) else 0
            decmial_part_length = markets[symbol]['precision']['price']
            total_length = integer_part_length + decmial_part_length
            if total_length > 4:
                selected_symbols.append(symbol)

        # selected_symbols = ['SUSHIUP/USDT']
        ohlcvs_limit = 1000

        # limit_step_ratios = np.arange(0.01, 0.05, 0.01)
        limit_step_ratios = [
            # 0.001,
            # 0.005,
            0.01,
            # 0.02,
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
            # 0.2,
            # 0.25,
        ]

        stoploss_safety_ratios = [
            # 0,
            # 0.2,
            0.25,
            # 0.3
        ]

        fee = 0.001

        results = []

        for symbol in selected_symbols:

            number_of_bad_candlestics = 0
            ohlcvs = self._public_client.fetch_ohlcv(symbol=symbol, limit=ohlcvs_limit)
            for ohlcv in ohlcvs:
                if not ((ohlcv[1] == ohlcv[3] and ohlcv[4] == ohlcv[2]) or (
                        ohlcv[1] == ohlcv[2] and ohlcv[4] == ohlcv[3])):
                    number_of_bad_candlestics += 1

            price_precision = markets[symbol]['precision']['price']
            amount_precision = markets[symbol]['precision']['amount']

            for r1 in limit_step_ratios:
                for r2 in stoploss2limit_ratios:
                    for r3 in stoploss_safety_ratios:

                        amount_in_quote = 100
                        closing_price = ohlcvs[0][4]
                        amount = truncate(((amount_in_quote * (1 - fee)) / closing_price), amount_precision)
                        amount_in_quote = 0
                        next_stoploss_price, next_stoploss_trigger_price, next_upper_buy_limit_price, next_lower_buy_limit_price = self._calculate_setup_prices(
                            closing_price, price_precision, r1, r2, r3)
                        number_of_upper_buy_limit_transactions = 0
                        number_of_lower_buy_limit_transactions = 0
                        number_of_stoploss_triggered_transactions = 0

                        for i in range(1, len(ohlcvs)):
                            openin_price = ohlcvs[i][1]
                            highest_price = ohlcvs[i][2]
                            lowest_price = ohlcvs[i][3]
                            next_closing_price = ohlcvs[i][4]

                            # .....................................................................

                            if next_closing_price > closing_price:
                                if next_closing_price > next_upper_buy_limit_price:
                                    if amount_in_quote:
                                        amount = truncate(
                                            ((amount_in_quote * (1 - fee)) / next_upper_buy_limit_price),
                                            amount_precision)
                                        amount_in_quote = 0
                                        number_of_upper_buy_limit_transactions += 1
                                    next_stoploss_price, next_stoploss_trigger_price, next_upper_buy_limit_price, next_lower_buy_limit_price = self._calculate_setup_prices(
                                        next_closing_price, price_precision, r1, r2, r3)

                            else:
                                if amount:
                                    if next_closing_price < next_stoploss_trigger_price:
                                        amount_in_quote = truncate(amount * (1 - fee) * next_stoploss_price,
                                                                   amount_precision)
                                        amount = 0
                                        number_of_stoploss_triggered_transactions += 1

                                if next_closing_price < next_lower_buy_limit_price:
                                    amount = truncate((amount_in_quote * (1 - fee)) / next_closing_price,
                                                      amount_precision)
                                    amount_in_quote = 0
                                    number_of_lower_buy_limit_transactions += 1
                                    next_stoploss_price, next_stoploss_trigger_price, next_upper_buy_limit_price, next_lower_buy_limit_price = self._calculate_setup_prices(
                                        next_closing_price, price_precision, r1, r2, r3)

                            closing_price = next_closing_price
                        total_number_of_transactions = number_of_lower_buy_limit_transactions + number_of_upper_buy_limit_transactions + number_of_stoploss_triggered_transactions
                        if amount:
                            amount_in_quote = amount * closing_price

                        results.append(
                            {
                                'symbol': symbol,
                                'limit_step_ratio': r1,
                                'stoploss2limit_ratio': r2,
                                'stoploss_safety_ratio': r3,
                                'profit_rate': ((amount_in_quote - 100) / 100) * 100,
                                'total_number_of_transactions': total_number_of_transactions,
                                'number_of_upper_buy_limit_transactions': number_of_upper_buy_limit_transactions,
                                'number_of_lower_buy_limit_transactions': number_of_lower_buy_limit_transactions,
                                'number_of_stoploss_triggered_transactions': number_of_stoploss_triggered_transactions,
                                'number_of_bad_candlestics': number_of_bad_candlestics,
                            }
                        )
        sorted_results = sorted(results, key=lambda k: k['profit_rate'], reverse=True)
        optimum_result = sorted_results[0]
        self._optimum_symbol = optimum_result['symbol']
        self._optimum_limit_step_ratio = optimum_result['limit_step_ratio']
        self._optimum_stoploss2limit_ratio = optimum_result['stoploss2limit_ratio']

    def _calculate_setup_prices(self, current_price,
                                price_precision,
                                limit_step_ratio,
                                stoploss2limit_ratio,
                                stoploss_safty_ratio):
        next_stoploss_price = round(current_price * (1 - limit_step_ratio * stoploss2limit_ratio), price_precision)
        next_stoploss_trigger_price = round(
            current_price * (1 - limit_step_ratio * stoploss2limit_ratio * (1 - stoploss_safty_ratio)), price_precision)
        next_upper_buy_limit_price = current_price
        next_lower_buy_limit_price = round(current_price * (1 - limit_step_ratio),
                                           price_precision)

        return next_stoploss_price, next_stoploss_trigger_price, next_upper_buy_limit_price, next_lower_buy_limit_price

    def _determine_senario(self,
                           previous_closing_price,
                           opening_price,
                           highest_price,
                           lowest_price,
                           closing_price,
                           nu,
                           sl,
                           nl):

        s = 0
        if previous_closing_price == nu:
            if closing_price > previous_closing_price:
                if opening_price == lowest_price:
                    if closing_price == highest_price:
                        s = 1
                    else:
                        s = 2
                else:
                    if lowest_price > sl:
                        if highest_price == closing_price:
                            s = 3
                        else:
                            s = 4
                    else:
                        pass
            else:
                pass
        else:
            pass
