import time
import asyncio
import websockets
from typing import List, Set
from django.db.models import Q
from global_utils import my_get_logger
from futures_trader.models import FuturesPosition, FuturesBot, FuturesStoploss
from futures_trader.clients import PublicClient, PrivateClient
from threading import Thread
from dataclasses import dataclass, field
from .strategies.strategy_center import FuturesStrategyCenter
from .models import FuturesSignal, FuturesStep, FuturesTarget
from global_utils import CustomException, CacheUtils, round_down, slash2dash
from websockets.exceptions import ConnectionClosedError
from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient
from futures_trader.utils import is_test


@dataclass
class PriceTicker:
    thread: Thread
    client: KucoinFuturesWsClient = None
    subscribers: Set = field(default_factory=lambda: set())

    def stop(self):
        pass

    def unsubscribe_bot(self, bot_id):
        if bot_id in self.subscribers:
            self.subscribers.remove(bot_id)

    def stop_if_no_subscribers(self):
        if not self.subscribers:
            self.stop()


class FuturesBotHandler:

    def __init__(self):
        self._bots = {}
        self._public_clients = {}
        self._price_tickers = {}

    def create_bot(self, exchange_id: str, credential_id: str, strategy: str, position_data: dict):

        strategy_developer = FuturesStrategyCenter.get_strategy_developer(strategy=strategy)
        strategy_developer.validate_position_data(position_data=position_data)

        signal = None
        signal_data = position_data.get('signal')
        if signal_data:
            signal = FuturesSignal(**{key: signal_data.get(key) for key in
                                      ['symbol', 'side']})

            stoploss_data = signal_data.get('stoploss')
            if stoploss_data:
                stoploss = FuturesStoploss(trigger_price=stoploss_data['trigger_price'])
                stoploss.save()
                signal.stoploss = stoploss

            step_share_set_mode = signal_data.get('step_share_set_mode', 'auto')

            signal.step_share_set_mode = step_share_set_mode
            signal.save()

            steps = []
            is_reversed = signal.side == 'sell'
            sorted_steps_data = sorted(signal_data['steps'], reverse=is_reversed, key=lambda s: s['entry_price'])
            if sorted_steps_data[0]['entry_price'] == -1:
                sorted_steps_data.append(sorted_steps_data.pop(0))

            for step_data in sorted_steps_data:
                step = FuturesStep(signal=signal,
                                   entry_price=step_data.get('entry_price'),
                                   share=round_down(step_data.get('share')))
                step.save()
                steps.append(step)

            signal.steps.set(steps)
            signal.related_steps = steps

            targets = []
            targets_data = signal_data.get('targets')
            if targets_data:
                is_reversed = signal.side == 'sell'
                sorted_targets_data = sorted(targets_data, reverse=is_reversed, key=lambda t: t['tp_price'])
                for target_data in sorted_targets_data:
                    target = FuturesTarget(signal=signal,
                                           tp_price=target_data.get('tp_price'))
                    target.save()
                    targets.append(target)

            signal.targets.set(targets)
            signal.related_targets = targets

        position = FuturesPosition(signal=signal,
                                   **{k: position_data[k] for k in ['margin']})

        position.leverage = position_data.get('leverage', '1')
        position.keep_open = position_data.get('keep_open', 'false') == 'true'
        position.save()

        new_bot = FuturesBot(exchange_id=exchange_id,
                             credential_id=credential_id,
                             strategy=strategy,
                             position=position)

        self.init_bot_requirements(bot=new_bot)
        strategy_developer = FuturesStrategyCenter.get_strategy_developer(new_bot.strategy)
        new_bot.set_strategy_state_data(strategy_developer.init_strategy_state_data(new_bot.position))
        new_bot.save()
        if credential_id in self._bots:
            self._bots[credential_id][str(new_bot.id)] = new_bot
        else:
            self._bots[credential_id] = {str(new_bot.id): new_bot}
        return new_bot

    def reload_bots(self):
        bots = list(FuturesBot.objects.filter(is_active=True))
        for bot in bots:
            self.init_bot_requirements(bot)
            self.set_bot_strategy_state_data(bot)
            if bot.credential_id in bots:
                self._bots[bot.credential_id][str(bot.id)] = bot
            else:
                self._bots[bot.credential_id] = {str(bot.id): bot}

    def set_bot_strategy_state_data(self, bot):
        strategy_developer = FuturesStrategyCenter.get_strategy_developer(bot.strategy)
        bot.set_strategy_state_data(strategy_developer.reload_strategy_state_data(bot.position))

    def init_bot_requirements(self, bot):
        private_client = PrivateClient(exchange_id=bot.exchange_id, credential_id=bot.credential_id)
        if bot.exchange_id in self._public_clients:
            public_client = self._public_clients[bot.exchange_id]
        else:
            public_client = PublicClient(exchange_id=bot.exchange_id)
            self._public_clients[bot.exchange_id] = public_client
        bot.init_requirements(private_client=private_client, public_client=public_client)
        bot.ready()

    def run_bots(self):
        while True:
            credentials = list(self._bots.keys())
            running_bots = []
            for credential in credentials:
                running_bots += [bot for bot in list(self._bots[credential].values())]
            for bot in running_bots:
                try:
                    if bot.status == FuturesBot.Status.RUNNING.value:
                        strategy_developer = FuturesStrategyCenter.get_strategy_developer(bot.strategy)
                        price_required_symbols = strategy_developer.get_strategy_symbols(bot.position)
                        symbol_prices = self._get_prices_if_available(bot.exchange_id, price_required_symbols)
                        while not symbol_prices:
                            if is_test:
                                self._start_muck_symbols_price_ticker(bot.exchange_id, price_required_symbols)
                            else:
                                self._start_symbols_price_ticker(bot.exchange_id, price_required_symbols)
                            time.sleep(15)
                            symbol_prices = self._get_prices_if_available(bot.exchange_id, price_required_symbols)

                        logger = my_get_logger()
                        logger.debug('symbol_prices: {}'.format(symbol_prices))

                        for symbol in price_required_symbols:
                            self._price_tickers[symbol].subscribers.add(bot.id)

                        operations = strategy_developer.get_operations(position=bot.position,
                                                                       strategy_state_data=bot.strategy_state_data,
                                                                       symbol_prices=symbol_prices)
                        bot.execute_operations(operations,
                                               bot.strategy_state_data,
                                               test=is_test)
                    if not bot.is_active:
                        self._bots[bot.credential_id].pop(str(bot.id))

                    if not bot.status == FuturesBot.Status.RUNNING.value:
                        price_ticker = self._price_tickers[bot.position.signal.symbol]
                        price_ticker.unsubscribe_bot(bot.id)
                        price_ticker.stop_if_no_subscribers()

                except Exception as e:
                    logger = my_get_logger()
                    logger.exception(e)
            time.sleep(1)

    def _get_prices_if_available(self, exchange_id, symbols: List):
        symbol_prices = self._read_prices(exchange_id, symbols)
        for symbol in symbols:
            if not (symbol in symbol_prices and symbol_prices[symbol]):
                return

        return symbol_prices

    def _start_muck_symbols_price_ticker(self, exchange_id, symbols: List):
        symbol_prices = self._read_prices(exchange_id, symbols)

        for symbol in symbols:
            if not (symbol in symbol_prices and symbol_prices[symbol]):
                t = Thread(target=asyncio.run, args=(self._start_muck_symbol_price_ticker(exchange_id, symbol),))
                self._price_tickers[symbol] = PriceTicker(t)
                t.start()

    async def _start_muck_symbol_price_ticker(self, exchange_id, symbol):
        uri = "ws://localhost:9001"
        cache_name = '{}_price'.format(exchange_id)

        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    price_ticker = self._price_tickers[symbol]
                    price_ticker.client = websocket
                    await websocket.send(symbol)
                    while True:
                        try:
                            price = await websocket.recv()
                            CacheUtils.write_to_cache(symbol, float(price), cache_name)
                        except Exception as e:
                            logger = my_get_logger()
                            logger.error(e)
                            break
            except (OSError, ConnectionClosedError):
                logger = my_get_logger()
                logger.warning('Could not connect to muck price server!')

    def _start_symbols_price_ticker(self, exchange_id, symbols: List):

        symbol_prices = self._read_prices(exchange_id, symbols)

        for symbol in symbols:
            if not (symbol in symbol_prices and symbol_prices[symbol]):
                if symbol not in self._price_tickers or self._price_tickers[symbol].client:
                    if symbol in self._price_tickers:
                        if exchange_id == 'kucoin':
                            self._price_tickers[symbol].stop()
                            logger = my_get_logger()
                            logger.warning('Error in price ticker was occurred!')

                    self._init_price_ticker(exchange_id, symbol)

    def _init_price_ticker(self, exchange_id, symbol):
        t = Thread(target=asyncio.run, args=(self._start_symbol_price_ticker(exchange_id, symbol),))
        self._price_tickers[symbol] = PriceTicker(t)
        t.start()

    async def _start_symbol_price_ticker(self, exchange_id, symbol):
        cache_name = '{}_price'.format(exchange_id)
        if exchange_id == 'kucoin':
            loop = asyncio.get_event_loop()

            async def deal_msg(msg):
                if msg['topic'] == '/market/ticker:{}'.format(slash2dash(symbol)):
                    CacheUtils.write_to_cache(symbol, float(msg['data']['price']), cache_name)

            client = WsToken()
            ws_client = await KucoinFuturesWsClient.create(loop, client, deal_msg, private=False)
            price_ticker = self._price_tickers[symbol]
            price_ticker.client = ws_client
            price_ticker.stop = lambda: asyncio.run(
                ws_client.unsubscribe('/market/ticker:{}'.format(slash2dash(symbol))))

            await ws_client.subscribe('/market/ticker:{}'.format(slash2dash(symbol)))
            while True:
                await asyncio.sleep(60, loop=loop)

    def _read_prices(self, exchange_id, symbols):
        cache_name = '{}_price'.format(exchange_id)
        return {
            symbol: CacheUtils.read_from_cache(symbol, cache_name) for symbol in symbols
        }

    def _run_strategy_developer_command(self, bot, strategy_developer, command, *args, **kwargs):
        method2run = getattr(strategy_developer, command)
        return method2run(bot.position, bot.strategy_state_data, *args, **kwargs)

    def get_active_bot(self, credential_id, bot_id):
        if credential_id in self._bots and bot_id in self._bots[credential_id]:
            bot = self._bots[credential_id][bot_id]
            if bot.credential_id == credential_id:
                return bot

    def get_bot(self, credential_id, bot_id):
        bot = self.get_active_bot(credential_id, bot_id)
        if not bot:
            bot = FuturesBot.objects.filter(Q(id=bot_id) & Q(credential_id=credential_id)).first()
        if bot:
            return bot
        raise CustomException('No bot with id {} was found for credential_id {}'.format(bot_id, credential_id))

    def get_bots(self, credential_id, is_active):
        if is_active:
            bots_dict: dict = self._bots.get(credential_id)
            if not bots_dict:
                raise CustomException('Not active bot was found for credential_id {}'.format(credential_id))
            bots = list(bots_dict.values())
        else:
            bots = FuturesBot.objects.filter(Q(credential_id=credential_id))
        for bot in bots:
            if bot.is_active:
                self.set_bot_strategy_state_data(bot)
        return bots

    def edit_position(self, credential_id, bot_id, new_position_data):
        bot = self.get_active_bot(credential_id, bot_id)
        if not bot:
            raise CustomException(
                'No active bot with id {} was found for credential_id {}'.format(bot_id, credential_id))

        strategy_developer = FuturesStrategyCenter.get_strategy_developer(bot.strategy)

        edited_data = []
        new_signal_data = new_position_data.get('signal')
        if new_signal_data:
            new_steps_data = new_signal_data.get('steps')
            if new_steps_data:
                steps_was_edited = self._run_strategy_developer_command(
                    bot,
                    strategy_developer,
                    'edit_steps',
                    new_steps_data,
                    new_signal_data.get('step_share_set_mode', 'auto'),
                )
                if steps_was_edited:
                    edited_data.append('steps')

            new_targets_data = new_signal_data.get('targets')
            if new_targets_data:
                targets_was_edited = self._run_strategy_developer_command(
                    bot,
                    strategy_developer,
                    'edit_targets',
                    new_targets_data,
                )
                if targets_was_edited:
                    edited_data.append('targets')

            new_stoploss = new_signal_data.get('stoploss')
            if new_stoploss:
                stoploss_was_edited = self._run_strategy_developer_command(
                    bot,
                    strategy_developer,
                    'edit_stoploss',
                    new_stoploss,
                )
                if stoploss_was_edited:
                    edited_data.append('stoploss')

        new_margin = new_position_data.get('margin')
        if new_margin:
            margin_was_edited = self._run_strategy_developer_command(
                bot,
                strategy_developer,
                'edit_margin',
                new_margin
            )
            if margin_was_edited:
                edited_data.append('margin')

        return bot.position, edited_data

    def pause_bot(self, credential_id, bot_id):
        bot = self.get_active_bot(credential_id, bot_id)
        if not bot:
            raise CustomException(
                'No active bot with id {} was found for credential_id {}'.format(bot_id, credential_id))

        if bot.status == FuturesBot.Status.PAUSED.value:
            raise CustomException('bot with id {} is already paused!'.format(bot_id))

        if bot.status == FuturesBot.Status.RUNNING.value:
            price_ticker = self._price_tickers[bot.position.signal.symbol]
            price_ticker.unsubscribe_bot(bot.id)
            price_ticker.stop_if_no_subscribers()

            bot.status = FuturesBot.Status.PAUSED.value
            bot.save()
            return bot

    def start_bot(self, credential_id, bot_id):
        bot = self.get_active_bot(credential_id, bot_id)
        if not bot:
            raise CustomException(
                'No active bot with id {} was found for credential_id {}'.format(bot_id, credential_id))

        if bot.status == FuturesBot.Status.RUNNING.value:
            raise CustomException('bot with id {} is already running!'.format(bot_id))

        if bot.status == FuturesBot.Status.PAUSED.value:
            bot.status = FuturesBot.Status.RUNNING.value
            bot.save()
            return bot

    def stop_bot(self, credential_id, bot_id):
        bot = self.get_active_bot(credential_id, bot_id)
        if not bot:
            raise CustomException(
                'No active bot with id {} was found for credential_id {}'.format(bot_id, credential_id))

        bot.status = FuturesBot.Status.STOPPED_MANUALY.value
        bot.is_active = False
        bot.close_position(test=is_test)
        bot.save()
        return bot
