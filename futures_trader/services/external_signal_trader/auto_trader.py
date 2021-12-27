import getpass
import asyncio
import queue
import time
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient, events
from futures_trader.services.trader import FuturesBotTrader
from .bnc_signal_extractor import extract_bnc_signal_data
from .black_whale_signal_extractor import extract_black_whale_signal_data
from .special_leverage_signal_extractor import extract_special_leverage_signal_data
from .killer_rat_signal_extractor import extract_killer_rat_signal_data
from .always_win_signal_extractor import extract_always_win_signal_data
from global_utils.retry_on_timeout import retry_on_timeout
from futures_trader.config import position_margin
from threading import Thread

signal_data_queue = queue.Queue()


@retry_on_timeout(timeout_errors=(ConnectionError,))
def create_client():
    api_id = 764667
    api_hash = 'ffb6562fd4311e1487c60f068f5b74ce'
    phone = '+989059242876'

    client = TelegramClient('{}.session'.format(phone), api_id, api_hash)

    client.connect()
    if not client.is_user_authorized():
        client.sign_in(phone)
        try:
            try:
                client.sign_in(code=input('Enter code: '))
            except SessionPasswordNeededError:
                client.sign_in(password=getpass.getpass())
        except EOFError:
            pass
    return client


signal_data_extractor_mapping = {
    1502962832: extract_bnc_signal_data,  # BNC
    1743103663: extract_black_whale_signal_data,  # BLACK WHALE
    1734497122: extract_special_leverage_signal_data,  # SPECIAL LEVERAGE
    1600174012: extract_killer_rat_signal_data,  # KILLER RAT
    1685166052: extract_always_win_signal_data,  # ALWAYS WIN
}


def get_source_channel_ids():
    return list(signal_data_extractor_mapping.keys())


def start_signal_receiving():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    myclient = create_client()

    @myclient.on(events.NewMessage(from_users=get_source_channel_ids()))
    async def extract_signal(event):
        channel_id = event.chat.id
        signal_data = signal_data_extractor_mapping[channel_id](event.message.message)
        if signal_data:
            signal_data_queue.put(signal_data)

    myclient.run_until_disconnected()


def consume_signal(signal_data):
    signal_data['setup_mode'] = 'auto'
    position_data = {
        'signal': signal_data,
        'margin': position_margin,
    }
    bot_data = {
        'exchange_id': 'kucoin',
        'credential_id': 'kucoin_main',
        'strategy': 'manual',
        'position': position_data,
    }
    FuturesBotTrader.create_bot(bot_data)


def start_signal_consuming():
    while True:
        if not signal_data_queue.empty():
            signal_data = signal_data_queue.get()
            consume_signal(signal_data)

        time.sleep(1)


def start_auto_trading():
    t1 = Thread(target=start_signal_receiving)
    t1.start()

    t2 = Thread(target=start_signal_consuming)
    t2.start()
