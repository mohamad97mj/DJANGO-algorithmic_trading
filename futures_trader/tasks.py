import gc
from celery import shared_task
from spot_trader.services.ta import TechnicalAnalyser
from fetch import symbols
from futures_trader.services.external_signal_trader.auto_trader import create_client
from spot_trader.clients import PublicClient
from futures_trader.clients import PrivateClient
from futures_trader.services.trader import FuturesBotTrader
from global_utils.my_logging import my_get_logger
from global_utils.catch_all_exceptions import catch_all_exceptions
from time import sleep
from global_utils import with2without_slash_f
from futures_trader.models import FuturesBot, FuturesSignal
from futures_trader.services.trader import bot_handler

myclient = create_client()


def notify_in_telegram(message):
    myclient.get_dialogs()
    entity = myclient.get_entity('My alarms')
    myclient.send_message(entity, message)


@shared_task
def technical_auto_trade():
    global myclient
    if not myclient:
        myclient = create_client()
    appropriate_symbols = []
    for symbol in symbols:
        result = auto_trader_per_symbol(symbol)
        if result:
            appropriate_symbols.append(result)
        sleep(1)

    message = 'appropriate symbols:{}\n'.format(appropriate_symbols)
    notify_in_telegram(message)
    gc.collect()


@catch_all_exceptions()
def auto_trader_per_symbol(symbol):
    cci, prev_cci = TechnicalAnalyser.get_cci(symbol=symbol,
                                              timeframe='1h',
                                              n=20)
    macd, prev_macd = TechnicalAnalyser.get_macd(symbol)
    bbd, bbu = TechnicalAnalyser.get_bollinger_band(symbol, timeframe='1h', n=20)
    pbc = PublicClient()
    ohlc = pbc.fetch_ohlcv(symbol, timeframe='1h', limit=1)[0]
    close = ohlc[4]
    confirmations = []
    is_signal = False

    if prev_cci < -100 < cci:
        is_signal = True
        confirmations.append('CCI')
        side = 'buy'
        risk = (close - bbd) / close
        reward = (bbu - close) / close
        rr = risk / reward
        if 0 < rr < 1 / 3:
            confirmations.append('Bollinger Bands')
        if macd > 0 and prev_macd > 0:
            confirmations.append('Trend')

    elif prev_cci > 100 > cci:
        is_signal = True
        confirmations.append('CCI')
        side = 'sell'
        risk = (bbu - close) / close
        reward = (close - bbd) / close
        rr = risk / reward
        if 0 < rr < 1 / 3:
            confirmations.append('Bollinger Bands')
        if macd < 0 and prev_macd < 0:
            confirmations.append('Trend')
    if is_signal:
        signal_data = {'symbol': symbol,
                       'side': side,
                       'confirmations': confirmations}
        FuturesSignal.objects.create(**signal_data)
        return symbol


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
