import gc
import datetime
from celery import shared_task
from spot_trader.services.ta import TechnicalAnalyser
from fetch import symbols
from futures_trader.services.external_signal_trader.auto_trader import create_client
from futures_trader.clients import PrivateClient, PublicClient as FuturesPublicClient
from futures_trader.services.trader import FuturesBotTrader
from global_utils.my_logging import my_get_logger
from global_utils.catch_all_exceptions import catch_all_exceptions
from time import sleep
from global_utils import with2without_slash_f
from futures_trader.models import FuturesBot, FuturesSignal
from futures_trader.services.trader import bot_handler
from spot_trader.clients import PublicClient as SpotPublicClient
from candlestick import detect_patterns_in_two_previous_candles, has_long_candlestick_confirmation, \
    has_short_candlestick_confirmation

myclient = create_client()


def notify_in_telegram(message, entity):
    myclient.get_dialogs()
    entity = myclient.get_entity(entity)
    myclient.send_message(entity, message)


@shared_task
def technical_auto_trade():
    global myclient
    if not myclient:
        myclient = create_client()
    datetime_str = datetime.datetime.now().strftime("%Y/%m/%d, %H") + ':30'
    notify_in_telegram(datetime_str, 'My logs')
    appropriate_symbols = []
    for symbol in symbols:
        result, data_log = auto_trader_per_symbol(symbol)
        if result:
            appropriate_symbols.append(symbol)
        notify_in_telegram(data_log, 'My logs')

    message = 'appropriate symbols:{}\n'.format(appropriate_symbols)
    notify_in_telegram(message, 'My alarms')
    gc.collect()


@catch_all_exceptions()
def auto_trader_per_symbol(symbol):
    logger = my_get_logger()
    # spot_public_client = SpotPublicClient()
    data_log = '''symbol: {},
prev cci: {},
cci: {},
prev macd: {},
macd: {},
previous candle patterns: {},
current candle patterns: {},
bbd: {},
bbu: {},
rr: {},
confirmations: {}'''
    cci, prev_cci = TechnicalAnalyser.get_cci(symbol)
    macd, prev_macd = TechnicalAnalyser.get_macd(symbol)
    bbd, bbu = TechnicalAnalyser.get_bollinger_band(symbol)
    previous_candle_patterns, current_candle_patterns = detect_patterns_in_two_previous_candles(symbol)
    close = FuturesPublicClient().fetch_ticker(symbol)

    data_log = data_log.format(
        symbol,
        prev_cci,
        cci,
        prev_macd,
        macd,
        str(previous_candle_patterns),
        str(current_candle_patterns),
        bbd,
        bbu,
        '{}',
        '{}',
    )

    rr = None
    confirmations = None

    watching_signal = FuturesSignal.objects.filter(symbol=symbol, status=FuturesSignal.Status.WATCHING.value).first()
    if watching_signal:
        if cci < -100 or cci > 100:
            watching_signal.status = FuturesSignal.Status.UNWATCHED.value
            watching_signal.save()
            data_log.format(rr, confirmations)
            data_log += '\nsignal watching status: {}'.format('unwatched')
            return False, data_log
        else:
            if cci > -100:
                risk = (close - bbd) / close
                reward = (bbu - close) / close
                rr = risk / reward
                if macd > 0 and prev_macd > 0 and 0 < rr < 2 and has_long_candlestick_confirmation(
                        previous_candle_patterns, current_candle_patterns):
                    watching_signal.status = FuturesSignal.Status.WATCHING.value
                    watching_signal.confirmations.append('Candlestick')
                    watching_signal.save()
                    data_log.format(rr, str(watching_signal.confirmations))
                    data_log += '\nsignal watching status: {}'.format('waiting')
                    return True, data_log
                else:
                    data_log.format(rr, confirmations)
                    return False, data_log
            else:
                risk = (bbu - close) / close
                reward = (close - bbd) / close
                rr = risk / reward
                if macd < 0 and prev_macd < 0 and 0 < rr < 2 and has_short_candlestick_confirmation(
                        previous_candle_patterns, current_candle_patterns):
                    watching_signal.status = FuturesSignal.Status.WATCHING.value
                    watching_signal.confirmations.append('Candlestick')
                    watching_signal.save()
                    data_log.format(rr, str(watching_signal.confirmations))
                    data_log += '\nsignal watching status: {}'.format('waiting')
                    return True, data_log
                else:
                    data_log.format(rr, confirmations)
                    return False, data_log

    else:
        if prev_cci < -100 < cci:
            confirmations = ['CCI']
            side = 'buy'
            if macd > 0 and prev_macd > 0:
                confirmations.append('Trend')
            risk = (close - bbd) / close
            reward = (bbu - close) / close
            rr = risk / reward
            if 0 < rr < 2:
                confirmations.append('Bollinger Bands')
            if has_long_candlestick_confirmation(previous_candle_patterns, current_candle_patterns):
                confirmations.append('Candlestick')
            data_log = data_log.format(
                rr,
                str(confirmations),
            )

        elif prev_cci > 100 > cci:
            confirmations = ['CCI']
            side = 'sell'
            if macd < 0 and prev_macd < 0:
                confirmations.append('Trend')
            risk = (bbu - close) / close
            reward = (close - bbd) / close
            rr = risk / reward
            if 0 < rr < 2:
                confirmations.append('Bollinger Bands')
            if has_short_candlestick_confirmation(previous_candle_patterns, current_candle_patterns):
                confirmations.append('Candlestick')
            data_log = data_log.format(
                rr,
                str(confirmations),
            )

        data_log = data_log.format(rr, confirmations)
        logger.debug(data_log)

        if confirmations and all(c in confirmations for c in ['CCI', 'Trend', 'Bollinger Bands']):
            # leverage = min(int(10 / (100 * risk)), 20)
            signal_data = {'symbol': symbol,
                           'side': side,
                           'confirmations': confirmations}
            if 'Candlestick' in confirmations:
                FuturesSignal.objects.create(**signal_data)
                return True, data_log
            else:
                signal_data['status'] = FuturesSignal.Status.WATCHING.value
                FuturesSignal.objects.create(**signal_data)
                data_log += '\nsignal watching status: {}'.format('watching')
                return False, data_log
            # signal_data = {'obj': signal,
            #                'steps': [{'entry_price': -1, }],
            #                'targets': [{'tp_price': tp1}, {'tp_price': tp2}],
            #                'stoploss': {'trigger_price': stoploss}}
            # position_data = {
            #     'signal': signal_data,
            #     'margin': 25,
            # }
            # bot_data = {
            #     'exchange_id': 'kucoin',
            #     'credential_id': 'kucoin_main',
            #     'strategy': 'manual',
            #     'position': position_data,
            # }
            # FuturesBotTrader.create_bot(bot_data)
            # signal.status = 'confirmed'
            # signal.save()
        return False, data_log


@shared_task
@catch_all_exceptions()
def cancel_remaining_orders():
    active_bots = bot_handler.reload_bots()
    prc = PrivateClient(exchange_id='kucoin', credential_id='kucoin_main')
    open_positions = prc.get_all_positions()
    open_positions = open_positions if isinstance(open_positions, list) else []
    for bot in active_bots:
        position = bot.position
        signal = position.signal
        for open_position in open_positions:
            if open_position['symbol'] == with2without_slash_f(signal.symbol):
                break
        else:
            if bot.status == FuturesBot.Status.RUNNING.value:
                prc.cancel_all_stop_orders(symbol=signal.symbol)
                prc.cancel_all_limit_orders(symbol=signal.symbol)
                bot.status = FuturesBot.Status.STOPPED.value
                bot.is_active = False
                bot.save()
