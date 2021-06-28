from dataclasses import dataclass
from trader.global_utils import truncate
from trader.clients.public_client import PublicClient
from trader.main.spot.models import SpotPosition


@dataclass
class RatioData:
    limit_step_ratio: str
    stoploss2limit_ratio: str
    stoploss_safty_ratio: str


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

        results = []

        for symbol in selected_symbols:

            ohlcvs = self._public_client.fetch_ohlcv(symbol=symbol, limit=ohlcvs_limit)

            price_precision = markets[symbol]['precision']['price']
            amount_precision = markets[symbol]['precision']['amount']
            fee = markets[symbol]['maker']

            symbol_market_data = SymbolMarketData(price_precision, amount_precision, fee)

            for r1 in limit_step_ratios:
                for r2 in stoploss2limit_ratios:
                    for r3 in stoploss_safety_ratios:
                        balnace_data = BalanceData(amount=0, amount_in_quote=100, is_cache=True)
                        shlc_data = ShlcData(ohlcvs[0][1], ohlcvs[0][2], ohlcvs[0][3], ohlcvs[0][4])
                        self._buy(balnace_data,
                                  shlc_data.starting_price,
                                  symbol_market_data.amount_precision,
                                  symbol_market_data.fee)

                        cache = False
                        stoploss_price, stoploss_trigger_price, upper_buy_limit_price, lower_buy_limit_price = self._calculate_setup_prices(
                            starting_price, price_precision, r1, r2, r3)

                        stoploss_price, stoploss_trigger_price, upper_buy_limit_price, lower_buy_limit_price, amount, amount_in_quote = self._update_candlestick_setup(
                            price_precision,
                            r1,
                            r2,
                            r3,
                            stoploss_price,
                            stoploss_trigger_price,
                            upper_buy_limit_price,
                            lower_buy_limit_price,
                            cache,
                            amount,
                            amount_in_quote,
                            starting_price,
                            highest_price,
                            lowest_price,
                            closing_price
                        )

                        for i in range(1, len(ohlcvs)):
                            previous_closing_price = closing_price
                            # opening_price = ohlcvs[i][1]
                            highest_price = ohlcvs[i][2]
                            lowest_price = ohlcvs[i][3]
                            closing_price = ohlcvs[i][4]

                            stoploss_price, stoploss_trigger_price, upper_buy_limit_price, lower_buy_limit_price, amount, amount_in_quote = self._update_candlestick_setup(
                                price_precision,
                                r1,
                                r2,
                                r3,
                                stoploss_price,
                                stoploss_trigger_price,
                                upper_buy_limit_price,
                                lower_buy_limit_price,
                                cache,
                                amount,
                                amount_in_quote,
                                previous_closing_price,
                                highest_price,
                                lowest_price,
                                closing_price,
                            )

                        if amount:
                            amount_in_quote = amount * closing_price

                        results.append(
                            {
                                'symbol': symbol,
                                'limit_step_ratio': r1,
                                'stoploss2limit_ratio': r2,
                                'stoploss_safety_ratio': r3,
                                'profit_rate': ((amount_in_quote - 100) / 100) * 100,
                                # 'total_number_of_transactions': total_number_of_transactions,
                                # 'number_of_upper_buy_limit_transactions': number_of_upper_buy_limit_transactions,
                                # 'number_of_lower_buy_limit_transactions': number_of_lower_buy_limit_transactions,
                                # 'number_of_stoploss_triggered_transactions': number_of_stoploss_triggered_transactions,
                            }
                        )

            sorted_results = sorted(results, key=lambda k: k['profit_rate'], reverse=True)
            optimum_result = sorted_results[0]
            self._optimum_symbol = optimum_result['symbol']
            self._optimum_limit_step_ratio = optimum_result['limit_step_ratio']
            self._optimum_stoploss2limit_ratio = optimum_result['stoploss2limit_ratio']

    def _buy(self, balanace_data, buy_amount_in_quote, buy_price, amount_precision, fee):
        pure_buy_amount_in_quote = buy_amount_in_quote * (1 - fee)
        buy_amount = truncate((pure_buy_amount_in_quote / buy_price), amount_precision)
        # remaining_amount_in_quote = pure_buy_amount_in_quote - buy_amount * buy_price
        remaining_amount_in_quote = 0
        balanace_data.is_cache = True
        balanace_data.amount += buy_amount
        balanace_data.amount_in_quote -= (buy_amount_in_quote - remaining_amount_in_quote)

    def _calculate_setup_prices(self,
                                current_price,
                                price_precision,
                                limit_step_ratio,
                                stoploss2limit_ratio,
                                stoploss_safty_ratio):
        stoploss_price = round(current_price * (1 - limit_step_ratio * stoploss2limit_ratio), price_precision)
        stoploss_trigger_price = round(
            current_price * (1 - limit_step_ratio * stoploss2limit_ratio * (1 - stoploss_safty_ratio)), price_precision)
        upper_buy_limit_price = current_price
        lower_buy_limit_price = round(current_price * (1 - limit_step_ratio), price_precision)

        return stoploss_price, stoploss_trigger_price, upper_buy_limit_price, lower_buy_limit_price

    def _update_candlestick_setup(self,
                                  price_precision,
                                  limit_step_ratio,
                                  stoploss2limit_ratio,
                                  stoploss_safty_ratio,
                                  stoploss_price,
                                  stoploss_trigger_price,
                                  upper_buy_limit_price,
                                  lower_buy_limit_price,
                                  cache,
                                  amount,
                                  amount_in_quote,
                                  amount_precision,
                                  fee,
                                  starting_price,
                                  highest_price,
                                  lowest_price,
                                  closing_price):

        senario = self._determine_senario(starting_price, highest_price, lowest_price, closing_price)

        if senario == 1:
            if cache:
                if upper_buy_limit_price < highest_price:
                    amount, amount_in_quote = self._buy(amount_in_quote,
                                                        upper_buy_limit_price,
                                                        amount_precision,
                                                        fee)
                    stoploss_price, stoploss_trigger_price, upper_buy_limit_price, lower_buy_limit_price = self._calculate_setup_prices(
                        closing_price, price_precision, limit_step_ratio, stoploss2limit_ratio, stoploss_safty_ratio)
                else:
                    pass
            else:
                stoploss_price, stoploss_trigger_price, upper_buy_limit_price, lower_buy_limit_price = self._calculate_setup_prices(
                    closing_price, price_precision, limit_step_ratio, stoploss2limit_ratio, stoploss_safty_ratio)

        elif senario == 2:
            pass

        return stoploss_price, stoploss_trigger_price, upper_buy_limit_price, lower_buy_limit_price, amount, amount_in_quote

    def _determine_senario(self,
                           starting_price,
                           highest_price,
                           lowest_price,
                           closing_price):

        if closing_price > starting_price:
            if lowest_price == starting_price:
                if highest_price == closing_price:
                    s = 1
                else:
                    s = 2
            else:
                if highest_price == closing_price:
                    s = 3
                else:
                    s = 4

        else:
            if highest_price == starting_price:
                if lowest_price == closing_price:
                    s = 5
                else:
                    s = 6
            else:
                if lowest_price == closing_price:
                    s = 7
                else:
                    s = 8

        return s

    def _update_ascending_setup(self, lowest_price, higest_price):
        pass

    def _update_descending_setup(self, highest_price, lowest_price):
        pass
