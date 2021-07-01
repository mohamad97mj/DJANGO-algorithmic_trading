from typing import List
from dataclasses import dataclass, field
from copy import deepcopy
from trader.global_utils import truncate, my_copy, intersection
from trader.clients.public_client import PublicClient
from trader.main.spot.models import SpotPosition, SpotOrder, Operation


@dataclass
class RatioData:
    limit_step_ratio: float
    stoploss2limit_ratio: float
    # stoploss_safety_ratio: float


@dataclass
class ShlcData:
    starting_price: float
    highest_price: float
    lowest_price: float
    closing_price: float


@dataclass
class SetupData:
    stoploss_price: float
    # stoploss_trigger_price: float
    upper_buy_limit_price: float
    lower_buy_limit_price: float


@dataclass
class BalanceData:
    amount: float
    amount_in_quote: float
    is_cash: bool


@dataclass
class SymbolMarketData:
    price_precision: int
    amount_precision: int
    fee: float


@dataclass
class ResultData:
    symbol: str = None
    limit_step_ratio: float = None
    stoploss2limit_ratio: float = None
    # stoploss_safety_ratio: float = None
    profit_rate: float = None
    total_number_of_transactions: int = None
    number_of_transactions: dict = field(default_factory=lambda: {
        'upper_buy_limit': 1,
        'lower_buy_limit': 0,
        'stoploss_triggered': 0
    })
    number_of_scenarios: dict = field(default_factory=lambda: {str(k): 0 for k in range(1, 9)})


@dataclass
class StateData:
    symbol: str = None
    price: float = None
    setup_data: SetupData = None
    balance_data: BalanceData = None


class StrategyStateData:
    states_data: List[StateData]


class TrailingStoplossStrategyDeveloper:

    def __init__(self, public_client):
        self._public_client = public_client
        self._test_init_optimum_parameters()

    def set_operations(self, position: SpotPosition, strategy_state_data: StrategyStateData):
        markets = self._public_client.get_markets()
        operations = []
        for state_data in strategy_state_data.states_data:
            if state_data.price > state_data.setup_data.upper_buy_limit_price:
                if state_data.balance_data.is_cash:
                    buy_order = SpotOrder(symbol=state_data.symbol,
                                          type='market',
                                          side='buy',
                                          price=state_data.price,
                                          amount_in_quote=state_data.balance_data.amount_in_quote, )
                    buy_order.save()
                    sell_operation = Operation(
                        order=buy_order,
                        action='create',
                        position=position,
                        status='in_progress')
                    operations.append(sell_operation)
                    sell_operation.save()
                    position.save()

                state_data.setup_data = self._calculate_setup_data(
                    setupe_price=state_data.price,
                    price_precision=markets[state_data.symbol]['precision']['price'],
                    ratio_data=self._optimum_ratio_data)

            elif state_data.price < state_data.setup_data.lower_buy_limit_price:
                buy_order = SpotOrder(symbol=state_data.symbol,
                                      type='market',
                                      side='buy',
                                      price=state_data.price,
                                      amount_in_quote=state_data.balance_data.amount_in_quote, )
                buy_order.save()
                sell_operation = Operation(
                    order=buy_order,
                    action='create',
                    position=position,
                    status='in_progress')
                operations.append(sell_operation)
                sell_operation.save()
                position.save()

                state_data.setup_data = self._calculate_setup_data(
                    setupe_price=state_data.price,
                    price_precision=markets[state_data.symbol]['precision']['price'],
                    ratio_data=self._optimum_ratio_data)

            elif state_data.price < state_data.setup_data.stoploss_price:
                sell_order = SpotOrder(symbol=state_data.symbol,
                                       type='market',
                                       side='sell',
                                       price=state_data.price,
                                       amount_in_quote=state_data.balance_data.amount_in_quote, )
                sell_order.save()
                sell_operation = Operation(
                    order=sell_order,
                    action='create',
                    position=position,
                    status='in_progress')
                operations.append(sell_operation)
                sell_operation.save()
                position.save()

        return operations

    def _real_init_optimum_parameters(self):
        pass

    def _test_init_optimum_parameters(self):
        print("in test init optimum")
        markets = self._public_client.get_markets()
        selected_symbols = self.select_symbols(markets)
        limit_step_ratios, stoploss2limit_ratios = self._init_ratios()

        # selected_symbols = ['BTCUP/USDT']
        ohlcvs_limits = [60, 240, 1000]
        max_limit = max(ohlcvs_limits)
        initial_amount_in_quote = 100

        positive_results = {k: {} for k in ohlcvs_limits}
        for symbol in selected_symbols:
            ohlcvs = self._public_client.fetch_ohlcv(symbol=symbol, limit=max_limit)
            for limit in ohlcvs_limits:
                results_data = []
                symbol_market_data = SymbolMarketData(price_precision=markets[symbol]['precision']['price'],
                                                      amount_precision=markets[symbol]['precision']['amount'],
                                                      fee=markets[symbol]['maker'])
                offset = max_limit - limit

                for r1 in limit_step_ratios:
                    for r2 in stoploss2limit_ratios:
                        result_data = ResultData(symbol=symbol,
                                                 limit_step_ratio=r1,
                                                 stoploss2limit_ratio=r2)
                        # for r3 in stoploss_safety_ratios:
                        balance_data = BalanceData(amount=0, amount_in_quote=initial_amount_in_quote, is_cash=True)
                        shlc_data = ShlcData(ohlcvs[offset][1],
                                             ohlcvs[offset][2],
                                             ohlcvs[offset][3],
                                             ohlcvs[offset][4])

                        ratio_data = RatioData(r1,
                                               r2,
                                               # r3
                                               )
                        self._buy(balance_data=balance_data,
                                  buy_amount_in_quote=balance_data.amount_in_quote,
                                  buy_price=shlc_data.starting_price,
                                  amount_precision=symbol_market_data.amount_precision,
                                  fee=symbol_market_data.fee)

                        setup_data = self._calculate_setup_data(setupe_price=shlc_data.starting_price,
                                                                price_precision=symbol_market_data.price_precision,
                                                                ratio_data=ratio_data)

                        setup_data = self._run_candlestick_scenario(setup_data,
                                                                    balance_data,
                                                                    shlc_data,
                                                                    symbol_market_data,
                                                                    ratio_data,
                                                                    result_data)

                        for i in range(1, limit):
                            previous_closing_price = shlc_data.closing_price
                            shlc_data = ShlcData(previous_closing_price,
                                                 ohlcvs[offset + i][2],
                                                 ohlcvs[offset + i][3],
                                                 ohlcvs[offset + i][4])

                            setup_data = self._run_candlestick_scenario(setup_data,
                                                                        balance_data,
                                                                        shlc_data,
                                                                        symbol_market_data,
                                                                        ratio_data,
                                                                        result_data)

                        if not balance_data.is_cash:
                            balance_data.amount_in_quote += balance_data.amount * shlc_data.closing_price
                        result_data.profit_rate = \
                            ((balance_data.amount_in_quote - initial_amount_in_quote) / initial_amount_in_quote) * 100
                        results_data.append(result_data)
                positive_results_data = [rd for rd in results_data if rd.profit_rate > 0]
                if positive_results_data:
                    positive_results[limit][symbol] = positive_results_data[0]
        positive_results_symbols = {
            k: list(v.keys()) for k, v in positive_results.items()
        }
        intersection_symbols = intersection(*list(positive_results_symbols.values()))
        symbol_avg_profit = {
        }
        for s in intersection_symbols:
            print(s)
            avg_profit = 0
            for l in ohlcvs_limits:
                print(s)
                avg_profit += positive_results[l][s].profit_rate
            avg_profit /= len(ohlcvs_limits)
            avg_profit = int(avg_profit)
            symbol_avg_profit[s] = avg_profit

        total_avg_profit = 0
        for ap in symbol_avg_profit.values():
            total_avg_profit += ap
        symbol_balance_shares = {
            s: ap / total_avg_profit for s, ap in symbol_avg_profit.items()
        }

        self._optimum_ratio_data = RatioData(limit_step_ratios[0], stoploss2limit_ratios[0])
        self._optimum_symbol_balance_shares = symbol_balance_shares

    def select_symbols(self, markets):
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
            decimal_part_length = markets[symbol]['precision']['price']
            total_length = integer_part_length + decimal_part_length
            if total_length > 4:
                selected_symbols.append(symbol)

        return selected_symbols

    def _init_ratios(self):

        # limit_step_ratios = np.arange(0.01, 0.05, 0.01)
        limit_step_ratios = [
            # 0.001,
            # 0.005,
            # 0.01,
            0.02,
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
            # 0.1,
            # 0.2,
            0.25,
        ]

        stoploss_safety_ratios = [
            # 0,
            # 0.2,
            0.25,
            # 0.3
        ]

        return limit_step_ratios, stoploss2limit_ratios, \
            # stoploss_safety_ratios

    def _buy(self, balance_data, buy_amount_in_quote, buy_price, amount_precision, fee):
        deviation = 0.0001
        truncated_buy_amount_before_fee = truncate(buy_amount_in_quote / (buy_price * (1 + deviation)),
                                                   amount_precision)
        pure_buy_amount = truncated_buy_amount_before_fee * (1 - fee)
        real_buy_amount_in_quote = truncated_buy_amount_before_fee * buy_price
        balance_data.is_cash = False
        balance_data.amount += pure_buy_amount
        balance_data.amount_in_quote -= real_buy_amount_in_quote

    def _sell(self, balance_data, sell_amount, sell_price, amount_precision, fee):
        deviation = 0.0001
        truncated_sell_amount_before_fee = truncate(sell_amount, amount_precision)
        pure_sell_amount = truncated_sell_amount_before_fee * (1 - fee)
        pure_sell_amount_in_quote = pure_sell_amount * (sell_price * (1 - deviation))
        balance_data.is_cash = True
        balance_data.amount_in_quote += pure_sell_amount_in_quote
        balance_data.amount -= truncated_sell_amount_before_fee

    def _calculate_setup_data(self, setupe_price, price_precision, ratio_data):
        stoploss_price = round(setupe_price * (1 - ratio_data.limit_step_ratio * ratio_data.stoploss2limit_ratio),
                               price_precision)
        # stoploss_trigger_price = round(
        #     setupe_price * (1 - ratio_data.limit_step_ratio * ratio_data.stoploss2limit_ratio * (
        #             1 - ratio_data.stoploss_safety_ratio)), price_precision)
        upper_buy_limit_price = setupe_price
        lower_buy_limit_price = round(setupe_price * (1 - ratio_data.limit_step_ratio), price_precision)

        return SetupData(stoploss_price,
                         # stoploss_trigger_price,
                         upper_buy_limit_price,
                         lower_buy_limit_price)

    def _run_candlestick_scenario(self, setup_data, balance_data, shlc_data, symbol_market_data, ratio_data,
                                  result_data):

        scenario = self._determine_scenario(shlc_data)
        result_data.number_of_scenarios[scenario] += 1
        run_scenario_method = getattr(self, '_run_scenario{}'.format(scenario))
        return run_scenario_method(setup_data, balance_data, shlc_data, symbol_market_data, ratio_data, result_data)

    def _determine_scenario(self, shlc_data):

        if shlc_data.closing_price > shlc_data.starting_price:
            if shlc_data.lowest_price == shlc_data.starting_price:
                if shlc_data.highest_price == shlc_data.closing_price:
                    s = '1'
                else:
                    s = '2'
            else:
                if shlc_data.highest_price == shlc_data.closing_price:
                    s = '3'
                else:
                    s = '4'

        else:
            if shlc_data.highest_price == shlc_data.starting_price:
                if shlc_data.lowest_price == shlc_data.closing_price:
                    s = '5'
                else:
                    s = '6'
            else:
                if shlc_data.lowest_price == shlc_data.closing_price:
                    s = '7'
                else:
                    s = '8'

        return s

    def _run_scenario1(self, setup_data, balance_data, shlc_data, symbol_market_data, ratio_data, result_data):
        return self._run_ascending_scenario(setup_data=setup_data,
                                            balance_data=balance_data,
                                            highest_price=shlc_data.highest_price,
                                            symbol_market_data=symbol_market_data,
                                            ratio_data=ratio_data,
                                            result_data=result_data)

    def _run_scenario2(self, setup_data, balance_data, shlc_data, symbol_market_data, ratio_data, result_data):
        setup_data = self._run_ascending_scenario(setup_data=setup_data,
                                                  balance_data=balance_data,
                                                  highest_price=shlc_data.highest_price,
                                                  symbol_market_data=symbol_market_data,
                                                  ratio_data=ratio_data,
                                                  result_data=result_data)

        return self._run_descending_scenario(setup_data=setup_data,
                                             balance_data=balance_data,
                                             lowest_price=shlc_data.closing_price,
                                             symbol_market_data=symbol_market_data,
                                             ratio_data=ratio_data,
                                             result_data=result_data)

    def _run_scenario3(self, setup_data, balance_data, shlc_data, symbol_market_data, ratio_data, result_data):
        setup_data = self._run_descending_scenario(setup_data=setup_data,
                                                   balance_data=balance_data,
                                                   lowest_price=shlc_data.lowest_price,
                                                   symbol_market_data=symbol_market_data,
                                                   ratio_data=ratio_data,
                                                   result_data=result_data)

        return self._run_ascending_scenario(setup_data=setup_data,
                                            balance_data=balance_data,
                                            highest_price=shlc_data.highest_price,
                                            symbol_market_data=symbol_market_data,
                                            ratio_data=ratio_data,
                                            result_data=result_data)

    def _run_scenario4(self, setup_data, balance_data, shlc_data, symbol_market_data, ratio_data, result_data):
        balance_data1 = deepcopy(balance_data)
        setup_data1 = deepcopy(setup_data)
        result_data1 = deepcopy(result_data)
        setup_data1 = self._run_descending_scenario(setup_data=setup_data1,
                                                    balance_data=balance_data1,
                                                    lowest_price=shlc_data.lowest_price,
                                                    symbol_market_data=symbol_market_data,
                                                    ratio_data=ratio_data,
                                                    result_data=result_data1)

        setup_data1 = self._run_ascending_scenario(setup_data=setup_data1,
                                                   balance_data=balance_data1,
                                                   highest_price=shlc_data.highest_price,
                                                   symbol_market_data=symbol_market_data,
                                                   ratio_data=ratio_data,
                                                   result_data=result_data1)

        setup_data1 = self._run_descending_scenario(setup_data=setup_data1,
                                                    balance_data=balance_data1,
                                                    lowest_price=shlc_data.closing_price,
                                                    symbol_market_data=symbol_market_data,
                                                    ratio_data=ratio_data,
                                                    result_data=result_data1)

        amount_in_quote1 = balance_data1.amount_in_quote + balance_data1.amount * shlc_data.closing_price

        balance_data2 = deepcopy(balance_data)
        setup_data2 = deepcopy(setup_data)
        result_data2 = deepcopy(result_data)
        setup_data2 = self._run_ascending_scenario(setup_data=setup_data2,
                                                   balance_data=balance_data2,
                                                   highest_price=shlc_data.highest_price,
                                                   symbol_market_data=symbol_market_data,
                                                   ratio_data=ratio_data,
                                                   result_data=result_data2)

        setup_data2 = self._run_descending_scenario(setup_data=setup_data2,
                                                    balance_data=balance_data2,
                                                    lowest_price=shlc_data.lowest_price,
                                                    symbol_market_data=symbol_market_data,
                                                    ratio_data=ratio_data,
                                                    result_data=result_data2)

        setup_data2 = self._run_ascending_scenario(setup_data=setup_data2,
                                                   balance_data=balance_data2,
                                                   highest_price=shlc_data.closing_price,
                                                   symbol_market_data=symbol_market_data,
                                                   ratio_data=ratio_data,
                                                   result_data=result_data2)

        amount_in_quote2 = balance_data2.amount_in_quote + balance_data2.amount * shlc_data.closing_price

        if amount_in_quote1 < amount_in_quote2:
            my_copy(balance_data1, balance_data)
            my_copy(result_data1, result_data)
            return setup_data1
        else:
            my_copy(balance_data2, balance_data)
            my_copy(result_data2, result_data)
            return setup_data2

    def _run_scenario5(self, setup_data, balance_data, shlc_data, symbol_market_data, ratio_data, result_data):
        return self._run_descending_scenario(setup_data=setup_data,
                                             balance_data=balance_data,
                                             lowest_price=shlc_data.lowest_price,
                                             symbol_market_data=symbol_market_data,
                                             ratio_data=ratio_data,
                                             result_data=result_data)

    def _run_scenario6(self, setup_data, balance_data, shlc_data, symbol_market_data, ratio_data, result_data):
        setup_data = self._run_descending_scenario(setup_data=setup_data,
                                                   balance_data=balance_data,
                                                   lowest_price=shlc_data.lowest_price,
                                                   symbol_market_data=symbol_market_data,
                                                   ratio_data=ratio_data,
                                                   result_data=result_data)

        return self._run_ascending_scenario(setup_data=setup_data,
                                            balance_data=balance_data,
                                            highest_price=shlc_data.closing_price,
                                            symbol_market_data=symbol_market_data,
                                            ratio_data=ratio_data,
                                            result_data=result_data)

    def _run_scenario7(self, setup_data, balance_data, shlc_data, symbol_market_data, ratio_data, result_data):
        setup_data = self._run_ascending_scenario(setup_data=setup_data,
                                                  balance_data=balance_data,
                                                  highest_price=shlc_data.highest_price,
                                                  symbol_market_data=symbol_market_data,
                                                  ratio_data=ratio_data,
                                                  result_data=result_data)

        return self._run_descending_scenario(setup_data=setup_data,
                                             balance_data=balance_data,
                                             lowest_price=shlc_data.lowest_price,
                                             symbol_market_data=symbol_market_data,
                                             ratio_data=ratio_data,
                                             result_data=result_data)

    def _run_scenario8(self, setup_data, balance_data, shlc_data, symbol_market_data, ratio_data, result_data):
        balance_data1 = deepcopy(balance_data)
        setup_data1 = deepcopy(setup_data)
        setup_data1 = self._run_ascending_scenario(setup_data=setup_data1,
                                                   balance_data=balance_data1,
                                                   highest_price=shlc_data.highest_price,
                                                   symbol_market_data=symbol_market_data,
                                                   ratio_data=ratio_data,
                                                   result_data=result_data)

        setup_data1 = self._run_descending_scenario(setup_data=setup_data1,
                                                    balance_data=balance_data1,
                                                    lowest_price=shlc_data.lowest_price,
                                                    symbol_market_data=symbol_market_data,
                                                    ratio_data=ratio_data,
                                                    result_data=result_data)

        setup_data1 = self._run_ascending_scenario(setup_data=setup_data1,
                                                   balance_data=balance_data1,
                                                   highest_price=shlc_data.closing_price,
                                                   symbol_market_data=symbol_market_data,
                                                   ratio_data=ratio_data,
                                                   result_data=result_data)

        amount_in_quote1 = balance_data1.amount_in_quote + balance_data1.amount * shlc_data.closing_price

        balance_data2 = deepcopy(balance_data)
        setup_data2 = deepcopy(setup_data)
        setup_data2 = self._run_descending_scenario(setup_data=setup_data2,
                                                    balance_data=balance_data2,
                                                    lowest_price=shlc_data.lowest_price,
                                                    symbol_market_data=symbol_market_data,
                                                    ratio_data=ratio_data,
                                                    result_data=result_data)

        setup_data2 = self._run_ascending_scenario(setup_data=setup_data2,
                                                   balance_data=balance_data2,
                                                   highest_price=shlc_data.highest_price,
                                                   symbol_market_data=symbol_market_data,
                                                   ratio_data=ratio_data,
                                                   result_data=result_data)

        setup_data2 = self._run_descending_scenario(setup_data=setup_data2,
                                                    balance_data=balance_data2,
                                                    lowest_price=shlc_data.closing_price,
                                                    symbol_market_data=symbol_market_data,
                                                    ratio_data=ratio_data,
                                                    result_data=result_data)

        amount_in_quote2 = balance_data2.amount_in_quote + balance_data2.amount * shlc_data.closing_price

        if amount_in_quote1 < amount_in_quote2:
            my_copy(balance_data1, balance_data)
            return setup_data1
        else:
            my_copy(balance_data2, balance_data)
            return setup_data2

    def _run_ascending_scenario(self, setup_data, balance_data, highest_price, symbol_market_data, ratio_data,
                                result_data):
        if setup_data.upper_buy_limit_price < highest_price:
            if balance_data.is_cash:
                self._buy(balance_data=balance_data,
                          buy_amount_in_quote=balance_data.amount_in_quote,
                          buy_price=setup_data.upper_buy_limit_price,
                          amount_precision=symbol_market_data.amount_precision,
                          fee=symbol_market_data.fee)
                result_data.number_of_transactions['upper_buy_limit'] += 1

            setup_data = self._calculate_setup_data(setupe_price=highest_price,
                                                    price_precision=symbol_market_data.price_precision,
                                                    ratio_data=ratio_data)
        return setup_data

    def _run_descending_scenario(self, setup_data, balance_data, lowest_price, symbol_market_data, ratio_data,
                                 result_data):

        if lowest_price < setup_data.stoploss_price:
            if not balance_data.is_cash:
                self._sell(balance_data=balance_data,
                           sell_amount=balance_data.amount,
                           sell_price=setup_data.stoploss_price,
                           amount_precision=symbol_market_data.amount_precision,
                           fee=symbol_market_data.fee)
                result_data.number_of_transactions['stoploss_triggered'] += 1

            if lowest_price < setup_data.lower_buy_limit_price:
                self._buy(balance_data=balance_data,
                          buy_amount_in_quote=balance_data.amount_in_quote,
                          buy_price=setup_data.lower_buy_limit_price,
                          amount_precision=symbol_market_data.amount_precision,
                          fee=symbol_market_data.fee)
                result_data.number_of_transactions['lower_buy_limit'] += 1

                setup_data = self._calculate_setup_data(setupe_price=setup_data.lower_buy_limit_price,
                                                        price_precision=symbol_market_data.price_precision,
                                                        ratio_data=ratio_data)

                setup_data = self._run_descending_scenario(
                    setup_data=setup_data,
                    balance_data=balance_data,
                    lowest_price=lowest_price,
                    symbol_market_data=symbol_market_data,
                    ratio_data=ratio_data,
                    result_data=result_data
                )

        return setup_data
