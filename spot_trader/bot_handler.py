import time
import asyncio
import websockets
from typing import List, Union, Set
from django.db.models import Q
from global_utils import async_retry_on_timeout, my_get_logger
from spot_trader.models import SpotPosition, SpotBot, SpotStoploss
from spot_trader.clients import PublicClient, PrivateClient
from global_utils import with2without_slash, CacheUtils, CustomException, round_down, slash2dash
from threading import Thread
from dataclasses import dataclass, field
from concurrent.futures._base import TimeoutError
from spot_trader.strategies import SpotStrategyCenter
from spot_trader.models import SpotSignal, SpotStep, SpotTarget
from websockets.exceptions import ConnectionClosedError
from kucoin.client import WsToken
from spot_trader.utils.kucoin_ws import MyKucoinWsClient
from spot_trader.utils.app_vars import is_test


@dataclass
class PriceTicker:
    thread: Thread
    client: Union[MyKucoinWsClient] = None
    subscribers: Set = field(default_factory=lambda: set())

    def stop(self):
        pass

    def unsubscribe_bot(self, bot_id):
        if bot_id in self.subscribers:
            self.subscribers.remove(bot_id)
        if not self.subscribers:
            self.stop()


class SpotBotHandler:

    def __init__(self):
        self._bots = {}
        self._public_clients = {}
        self._price_tickers = {}

    def create_bot(self, exchange_id: str, credential_id: str, strategy: str, position_data: dict):

        strategy_developer = SpotStrategyCenter.get_strategy_developer(strategy=strategy)
        strategy_developer.validate_position_data(position_data=position_data)

        signal = None
        signal_data = position_data.get('signal')
        if signal_data:

            signal = SpotSignal(**{key: signal_data.get(key) for key in
                                   ['symbol']})

            stoploss_data = signal_data.get('stoploss')
            if stoploss_data:
                stoploss = SpotStoploss(trigger_price=stoploss_data['trigger_price'])
                stoploss.save()
                signal.stoploss = stoploss

            step_share_set_mode = signal_data.get('step_share_set_mode', 'auto')

            signal.setup_mode = step_share_set_mode
            signal.save()

            steps = []
            first_step_is_market = False
            sorted_steps_data = sorted(signal_data['steps'], key=lambda s: s['buy_price'])
            if sorted_steps_data[0]['buy_price'] == -1:
                sorted_steps_data.append(sorted_steps_data.pop(0))

            for step_data in sorted_steps_data:
                step = SpotStep(signal=signal,
                                buy_price=step_data.get('buy_price'),
                                share=round_down(step_data.get('share')))
                step.save()
                steps.append(step)

            signal.steps.set(steps)
            signal.related_steps = steps

            targets = []
            targets_data = signal_data.get('targets')
            if targets_data:
                sorted_targets_data = sorted(targets_data, key=lambda t: t['tp_price'])
                for target_data in sorted_targets_data:
                    target = SpotTarget(signal=signal,
                                        tp_price=target_data.get('tp_price'),
                                        share=round_down(target_data.get('share')))
                    target.save()
                    targets.append(target)

            signal.targets.set(targets)
            signal.related_targets = targets

        position = SpotPosition(signal=signal,
                                **{k: position_data[k] for k in ['amount_in_quote']})

        position.keep_open = position_data.get('keep_open', 'false') == 'true'
        position.save()

        new_bot = SpotBot(exchange_id=exchange_id,
                          credential_id=credential_id,
                          strategy=strategy,
                          position=position)

        self.init_bot_requirements(bot=new_bot)
        strategy_developer = SpotStrategyCenter.get_strategy_developer(new_bot.strategy)
        new_bot.set_strategy_state_data(strategy_developer.init_strategy_state_data(new_bot.position))
        new_bot.save()
        if credential_id in self._bots:
            self._bots[credential_id][str(new_bot.id)] = new_bot
        else:
            self._bots[credential_id] = {str(new_bot.id): new_bot}
        return new_bot

    def reload_bots(self):
        bots = list(SpotBot.objects.filter(is_active=True))
        for bot in bots:
            self.init_bot_requirements(bot)
            self.set_bot_strategy_state_data(bot)
            if bot.credential_id in self._bots:
                self._bots[bot.credential_id][str(bot.id)] = bot
            else:
                self._bots[bot.credential_id] = {str(bot.id): bot}

    def set_bot_strategy_state_data(self, bot):
        strategy_developer = SpotStrategyCenter.get_strategy_developer(bot.strategy)
        bot.set_strategy_state_data(strategy_developer.reload_setup(bot.position))

    def init_public_client(self, exchange_id):
        if exchange_id in self._public_clients:
            public_client = self._public_clients[exchange_id]
        else:
            public_client = PublicClient(exchange_id=exchange_id)
            self._public_clients[exchange_id] = public_client
        return public_client

    def init_bot_requirements(self, bot):
        private_client = PrivateClient(exchange_id=bot.exchange_id, credential_id=bot.credential_id)
        public_client = self.init_public_client(exchange_id=bot.exchange_id)
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
                    if bot.status == SpotBot.Status.RUNNING.value:
                        strategy_developer = SpotStrategyCenter.get_strategy_developer(bot.strategy)
                        price_required_symbols = strategy_developer.get_strategy_symbols(bot.position)
                        symbol_prices = self._get_prices_if_available(bot.exchange_id, price_required_symbols)
                        while not symbol_prices:
                            if is_test:
                                self._start_muck_symbols_price_ticker(bot.exchange_id, price_required_symbols)
                            else:
                                self._start_symbols_price_ticker(bot.exchange_id, price_required_symbols)
                            time.sleep(10)
                            symbol_prices = self._get_prices_if_available(bot.exchange_id, price_required_symbols)

                        logger = my_get_logger()
                        logger.debug('symbol_prices: {}'.format(symbol_prices))

                        for symbol in price_required_symbols:
                            self._price_tickers[symbol].subscribers.add(bot.id)

                        operations = strategy_developer.get_operations(position=bot.position,
                                                                       strategy_state_data=bot.strategy_state_data,
                                                                       symbol_prices=symbol_prices)

                        bot.execute_operations(operations, test=is_test)

                    if not bot.is_active:
                        self._bots[bot.credential_id].pop(str(bot.id))

                    if not bot.status == SpotBot.Status.RUNNING.value:
                        price_ticker = self._price_tickers[bot.position.signal.symbol]
                        price_ticker.unsubscribe_bot(bot.id)

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
        uri = "ws://localhost:9000"
        cache_name = '{}_spot_price'.format(exchange_id)
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
                    self._price_tickers[symbol].stop()
                    if not is_test:
                        logger = my_get_logger()
                        logger.warning('Error in spot price ticker was occurred!')

                    self._init_price_ticker(exchange_id, symbol)

    def _init_price_ticker(self, exchange_id, symbol):
        t = Thread(target=asyncio.run, args=(self._start_symbol_price_ticker(exchange_id, symbol),))
        self._price_tickers[symbol] = PriceTicker(t)
        t.start()

    async def _start_symbol_price_ticker(self, exchange_id, symbol):
        cache_name = '{}_spot_price'.format(exchange_id)
        if exchange_id == 'kucoin':
            loop = asyncio.get_event_loop()

            async def deal_msg(msg):
                if msg['topic'] == '/market/ticker:{}'.format(slash2dash(symbol)):
                    CacheUtils.write_to_cache(symbol, float(msg['data']['price']), cache_name)

            client = WsToken()
            ws_client = await MyKucoinWsClient.create(loop, client, deal_msg, private=False)

            price_ticker = self._price_tickers[symbol]
            price_ticker.client = ws_client

            def close_ws():
                # asyncio.run(ws_client.unsubscribe('/market/ticker:{}'.format(slash2dash(symbol))))
                ws_client.close_connection()

            price_ticker.stop = close_ws

            await ws_client.subscribe('/market/ticker:{}'.format(slash2dash(symbol)))
            while True:
                await asyncio.sleep(60, loop=loop)

    def _read_prices(self, exchange_id, symbols):
        cache_name = '{}_spot_price'.format(exchange_id)
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
            bot = SpotBot.objects.filter(Q(id=bot_id) & Q(credential_id=credential_id)).first()
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
            bots = SpotBot.objects.filter(Q(credential_id=credential_id))
        for bot in bots:
            if bot.is_active:
                self.set_bot_strategy_state_data(bot)
        return bots

    def edit_position(self, credential_id, bot_id, new_position_data):
        bot = self.get_active_bot(credential_id, bot_id)
        if not bot:
            raise CustomException(
                'No active bot with id {} was found for credential_id {}'.format(bot_id, credential_id))

        strategy_developer = SpotStrategyCenter.get_strategy_developer(bot.strategy)

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

        new_amount_in_quote = new_position_data.get('amount_in_quote')
        if new_amount_in_quote:
            amount_in_quote_was_edited = self._run_strategy_developer_command(
                bot,
                strategy_developer,
                'edit_amount_in_quote',
                new_amount_in_quote
            )
            if amount_in_quote_was_edited:
                edited_data.append('amount_in_quote')

        return bot.position, edited_data

    def pause_bot(self, credential_id, bot_id):
        bot = self.get_active_bot(credential_id, bot_id)
        if not bot:
            raise CustomException(
                'No active bot with id {} was found for credential_id {}'.format(bot_id, credential_id))

        if bot.status == SpotBot.Status.PAUSED.value:
            raise CustomException('bot with id {} is already paused!'.format(bot_id))

        if bot.status == SpotBot.Status.RUNNING.value:
            price_ticker = self._price_tickers[bot.position.signal.symbol]
            price_ticker.unsubscribe_bot(bot.id)

            bot.status = SpotBot.Status.PAUSED.value
            bot.save()
            return bot

    def start_bot(self, credential_id, bot_id):
        bot = self.get_active_bot(credential_id, bot_id)
        if not bot:
            raise CustomException(
                'No active bot with id {} was found for credential_id {}'.format(bot_id, credential_id))

        if bot.status == SpotBot.Status.RUNNING.value:
            raise CustomException('bot with id {} is already running!'.format(bot_id))

        if bot.status == SpotBot.Status.PAUSED.value:
            bot.status = SpotBot.Status.RUNNING.value
            bot.save()
            return bot

    def stop_bot(self, credential_id, bot_id):
        bot = self.get_active_bot(credential_id, bot_id)
        if not bot:
            raise CustomException(
                'No active bot with id {} was found for credential_id {}'.format(bot_id, credential_id))

        bot.status = SpotBot.Status.STOPPED_MANUALY.value
        bot.is_active = False
        bot.close_position(test=is_test)
        bot.save()
        return bot
