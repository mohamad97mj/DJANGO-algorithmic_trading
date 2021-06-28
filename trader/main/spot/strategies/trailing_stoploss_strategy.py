from dataclasses import dataclass
from trader.global_utils import truncate
from trader.clients.public_client import PublicClient
from trader.main.spot.models import SpotPosition


@dataclass
class RatioData:
    limit_step_ratio: float
    stoploss2limit_ratio: float
    stoploss_safty_ratio: float


@dataclass
class ShlcData:
    starting_price: float
    higheest_price: float
    lowest_price: float
    closing_price: float


@dataclass
class SetupData:
    stoploss_price: float
    stoploss_trigger_price: float
    upper_buy_limit_price: float
    lower_buy_limit_price: float


@dataclass
class BalanceData:
    amount: float
    amount_in_quote: float
    is_cache: bool


@dataclass
class SymbolMarketData:
    price_precision: int
    amount_precision: int
    fee: float


@dataclass
class ResultData:
    symbol: str
    limit_step_ratio: float
    stoploss2limit_ratio: float
    stoploss_safty_ratio: float
    profit_rata: float
    # total_number_of_transactions: int
    # number_of_upper_buy_limit_transactions: int
    # number_of_lower_buy_limit_transactions: int
    # number_of_stoploss_triggered_transactions: int


class TrailingStoplossStrategyDeveolper:

    def __init__(self, exchange_id):
        self._public_client = PublicClient(exchange_id)
        self._init_optimum_parameters()

    def set_operations(self, position: SpotPosition):
        pass

    def _init_optimum_parameters(self):
        markets = self._public_client.get_markets()
        selected_symbols = self.select_symbols(markets)
        limit_step_ratios, stoploss2limit_ratios, stoploss_safety_ratios = self._init_ratios()

        # selected_symbols = ['BTCUP/USDT']
        ohlcvs_limit = 1000

        results = []

        for symbol in selected_symbols:

            ohlcvs = self._public_client.fetch_ohlcv(symbol=symbol, limit=ohlcvs_limit)

            symbol_market_data = SymbolMarketData(price_precision=markets[symbol]['precision']['price'],
                                                  amount_precision=markets[symbol]['precision']['amount'],
                                                  fee=markets[symbol]['maker'])

            for r1 in limit_step_ratios:
                for r2 in stoploss2limit_ratios:
                    for r3 in stoploss_safety_ratios:
                        balanace_data = BalanceData(amount=0, amount_in_quote=100, is_cache=True)
                        shlc_data = ShlcData(ohlcvs[0][1], ohlcvs[0][2], ohlcvs[0][3], ohlcvs[0][4])
                        ratio_data = RatioData(r1, r2, r3)
                        self._buy(balanace_data,
                                  balanace_data.amount_in_quote,
                                  shlc_data.starting_price,
                                  symbol_market_data.amount_precision,
                                  symbol_market_data.fee)

                        setup_data = self._calculate_setup_data(current_price=shlc_data.starting_price,
                                                                price_precision=symbol_market_data.price_precision,
                                                                ratio_data=ratio_data)

                        self._run_candlestick_senario(
                            balanace_data,
                            symbol_market_data,
                            ratio_data,
                            setup_data,
                            shlc_data)

                        for i in range(1, len(ohlcvs)):
                            previous_closing_price = shlc_data.closing_price
                            shlc_data = (previous_closing_price, ohlcvs[i][2], ohlcvs[i][3], ohlcvs[i][4])

                            self._run_candlestick_senario(
                                balanace_data,
                                symbol_market_data,
                                ratio_data,
                                setup_data,
                                shlc_data)

                        if balanace_data.is_cache:
                            balanace_data.amount_in_quote = balanace_data.amount * shlc_data.closing_price

                        results.append(
                            ResultData(
                                symbol=symbol,
                                limit_step_ratio=r1,
                                stoploss2limit_ratio=r2,
                                stoploss_safty_ratio=r3,
                                profit_rata=((balanace_data.amount_in_quote - 100) / 100) * 100,
                                # total_number_of_transactions=total_number_of_transactions,
                                # number_of_upper_buy_limit_transactions=number_of_upper_buy_limit_transactions,
                                # number_of_lower_buy_limit_transactions=number_of_lower_buy_limit_transactions,
                                # number_of_stoploss_triggered_transactions=number_of_stoploss_triggered_transactions,
                            )
                        )

            sorted_results = sorted(results, key=lambda result: result.profit_rate, reverse=True)
            optimum_result = sorted_results[0]
            self._optimum_symbol = optimum_result.symbol
            self._optimum_limit_step_ratio = optimum_result.limit_step_ratio
            self._optimum_stoploss2limit_ratio = optimum_result.stoploss2limit_ratio

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
            decmial_part_length = markets[symbol]['precision']['price']
            total_length = integer_part_length + decmial_part_length
            if total_length > 4:
                selected_symbols.append(symbol)

        return selected_symbols

    def _init_ratios(self):

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

        return limit_step_ratios, stoploss2limit_ratios, stoploss_safety_ratios

    def _buy(self, balanace_data, buy_amount_in_quote, buy_price, amount_precision, fee):
        pure_buy_amount_in_quote = buy_amount_in_quote * (1 - fee)
        buy_amount = truncate((pure_buy_amount_in_quote / buy_price), amount_precision)
        # remaining_amount_in_quote = pure_buy_amount_in_quote - buy_amount * buy_price
        remaining_amount_in_quote = 0
        balanace_data.is_cache = True
        balanace_data.amount += buy_amount
        balanace_data.amount_in_quote -= (buy_amount_in_quote - remaining_amount_in_quote)

    def _calculate_setup_data(self,
                              current_price,
                              price_precision,
                              ratio_data):
        stoploss_price = round(current_price * (1 - ratio_data.limit_step_ratio * ratio_data.stoploss2limit_ratio),
                               price_precision)
        stoploss_trigger_price = round(
            current_price * (1 - ratio_data.limit_step_ratio * ratio_data.stoploss2limit_ratio * (
                    1 - ratio_data.stoploss_safty_ratio)), price_precision)
        upper_buy_limit_price = current_price
        lower_buy_limit_price = round(current_price * (1 - ratio_data.limit_step_ratio), price_precision)

        return SetupData(stoploss_price, stoploss_trigger_price, upper_buy_limit_price, lower_buy_limit_price)

    def _run_candlestick_senario(self,
                                 balance_data,
                                 symbol_market_data,
                                 ratio_data,
                                 setup_data,
                                 shlc_data):

        senario = self._determine_senario(shlc_data)

        if senario == 1:
            if balance_data.cache:
                if setup_data.upper_buy_limit_price < shlc_data.highest_price:
                    self._buy(balance_data,
                              balance_data.amount_in_quote,
                              setup_data.upper_buy_limit_price,
                              symbol_market_data.amount_precision,
                              symbol_market_data.fee)
                    setup_data = self._calculate_setup_data(
                        shlc_data.closing_price, symbol_market_data.price_precision, ratio_data)
            else:
                setup_data = self._calculate_setup_data(
                    shlc_data.closing_price, symbol_market_data.price_precision, ratio_data)

        elif senario == 2:
            pass

    def _determine_senario(self,
                           shlc_data):

        if shlc_data.closing_price > shlc_data.starting_price:
            if shlc_data.lowest_price == shlc_data.starting_price:
                if shlc_data.highest_price == shlc_data.closing_price:
                    s = 1
                else:
                    s = 2
            else:
                if shlc_data.highest_price == shlc_data.closing_price:
                    s = 3
                else:
                    s = 4

        else:
            if shlc_data.highest_price == shlc_data.starting_price:
                if shlc_data.lowest_price == shlc_data.closing_price:
                    s = 5
                else:
                    s = 6
            else:
                if shlc_data.lowest_price == shlc_data.closing_price:
                    s = 7
                else:
                    s = 8

        return s

    def _update_ascending_setup(self, lowest_price, higest_price):
        pass

    def _update_descending_setup(self, highest_price, lowest_price):
        pass
