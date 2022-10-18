import gc
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
    appropriate_symbols = []
    for symbol in symbols:
        result, data_log = auto_trader_per_symbol(symbol)
        if result:
            appropriate_symbols.append(result)
        notify_in_telegram(data_log, 'My logs')
        sleep(1)

    message = 'appropriate symbols:{}\n'.format(appropriate_symbols)
    notify_in_telegram(message, 'My alarms')
    gc.collect()


@catch_all_exceptions()
def auto_trader_per_symbol(symbol):
    logger = my_get_logger()
    # spot_public_client = SpotPublicClient()
    data_log = '''symbol: {},
prev_cci: {},
cci: {},
prev_macd: {},
macd: {},
bbd: {},
bbu: {},
rr: {},
previous_candle_patterns: {},
current_candle_patterns: {},
confirmations: {}'''
    cci, prev_cci = TechnicalAnalyser.get_cci(symbol)
    macd, prev_macd = TechnicalAnalyser.get_macd(symbol)
    bbd, bbu = TechnicalAnalyser.get_bollinger_band(symbol)
    previous_candle_patterns, current_candle_patterns = detect_patterns_in_two_previous_candles(symbol)
    close = FuturesPublicClient().fetch_ticker(symbol)
    confirmations = []

    rr = None
    if prev_cci < -100 < cci:
        confirmations.append('CCI')
        side = 'buy'
        risk = (close - bbd) / close
        # stoploss = bbd
        # tp1 = tp2 = close * (1 + 2 * risk)
        reward = (bbu - close) / close
        rr = risk / reward
        if 0 < rr < 2:
            confirmations.append('Bollinger Bands')
        if macd > 0 and prev_macd > 0:
            confirmations.append('Trend')
        if has_long_candlestick_confirmation(previous_candle_patterns, current_candle_patterns):
            confirmations.append('Candlestick')

    elif prev_cci > 100 > cci:
        confirmations.append('CCI')
        side = 'sell'
        risk = (bbu - close) / close
        # stoploss = bbu
        # tp1 = tp2 = close * (1 - 2 * risk)
        reward = (close - bbd) / close
        rr = risk / reward
        if 0 < rr < 2:
            confirmations.append('Bollinger Bands')
        if macd < 0 and prev_macd < 0:
            confirmations.append('Trend')
        if has_short_candlestick_confirmation(previous_candle_patterns, current_candle_patterns):
            confirmations.append('Candlestick')
    data_log = data_log.format(
        symbol,
        prev_cci,
        cci,
        prev_macd,
        macd,
        bbd,
        bbu,
        rr,
        str(previous_candle_patterns),
        str(current_candle_patterns),
        str(confirmations),
    )

    logger.debug(data_log)

    if len(confirmations) == 4:
        # leverage = min(int(10 / (100 * risk)), 20)
        signal_data = {'symbol': symbol,
                       'side': side,
                       'confirmations': confirmations}
        FuturesSignal.objects.create(**signal_data)
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
        return True, data_log
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
