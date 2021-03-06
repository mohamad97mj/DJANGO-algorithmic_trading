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
from futures_trader.strategies.strategy_center import FuturesStrategyCenter
from futures_trader.models import FuturesSignal, FuturesStep, FuturesTarget
from global_utils import CustomException, CacheUtils, round_down, async_retry_on_timeout, with2without_slash_f
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from kucoin_futures.client import WsToken
from futures_trader.services.utils.kucoin_ws import MyKucoinFuturesWsClient
from futures_trader.utils.app_vars import is_test
from concurrent.futures._base import TimeoutError
from futures_trader.config import max_number_of_risky_bots


@dataclass
class PriceTicker:
    id: int
    thread: Thread
    client: MyKucoinFuturesWsClient = None
    subscribers: Set = field(default_factory=lambda: set())

    def stop(self):
        pass

    def unsubscribe_bot(self, bot_id):
        if bot_id in self.subscribers:
            self.subscribers.remove(bot_id)
        if not self.subscribers:
            self.stop()


class FuturesBotHandler:

    def __init__(self):
        self._bots = {}
        self._public_clients = {}
        self._price_tickers = {}
        self.number_of_tickers = 0

    def create_bot(self, exchange_id: str, credential_id: str, strategy: str, position_data: dict):

        if self.validate_bot_data(exchange_id, credential_id, position_data['signal']['symbol']):

            strategy_developer = FuturesStrategyCenter.get_strategy_developer(strategy=strategy)
            strategy_developer.validate_position_data(position_data=position_data)

            signal_data = position_data.get('signal')
            signal = FuturesSignal(**{key: signal_data.get(key) for key in
                                      ['symbol', 'side', 'leverage']})
            signal.source = signal_data.get('source', 'manual')

            stoploss_data = signal_data.get('stoploss')
            if stoploss_data:
                stoploss = FuturesStoploss(trigger_price=stoploss_data['trigger_price'])
                stoploss.save()
                signal.stoploss = stoploss

            setup_mode = signal_data.get('setup_mode', 'auto')

            signal.setup_mode = setup_mode
            signal.save()

            position = FuturesPosition(signal=signal,
                                       **{k: position_data[k] for k in ['margin', 'order_type']})

            position.keep_open = position_data.get('keep_open', 'false') == 'true'

            steps = []
            first_step_is_market = False
            sort_steps_reverse = signal.side == 'buy'
            sorted_steps_data = sorted(signal_data['steps'], reverse=sort_steps_reverse, key=lambda s: s['entry_price'])
            if signal.side == 'buy':
                possibly_market_step_data = sorted_steps_data[len(sorted_steps_data) - 1]
            else:
                possibly_market_step_data = sorted_steps_data[0]
            if possibly_market_step_data['entry_price'] == -1:
                first_step_is_market = True
                public_client = self.get_public_client(exchange_id=exchange_id)
                possibly_market_step_data['entry_price'] = public_client.fetch_ticker(signal.symbol)
                if signal.side == 'buy':
                    sorted_steps_data.insert(0, sorted_steps_data.pop())

            sorted_steps_data_len = len(sorted_steps_data)
            auto_step_share = round_down(1 / sorted_steps_data_len)
            for i in range(sorted_steps_data_len):
                step_data = sorted_steps_data[i]
                if setup_mode == 'manual':
                    share = round_down(step_data.get('share'))
                else:
                    share = round(1 - (sorted_steps_data_len - 1) * auto_step_share, 2) \
                        if i == sorted_steps_data_len - 1 else auto_step_share
                step = FuturesStep(signal=signal,
                                   entry_price=step_data.get('entry_price'),
                                   share=share,
                                   margin=position.margin * share,
                                   is_market=first_step_is_market if i == 0 and first_step_is_market else False)
                step.save()
                steps.append(step)

            signal.steps.set(steps)
            signal.related_steps = steps
            position.save()
            targets = []
            targets_data = signal_data.get('targets')
            if targets_data:
                sort_targets_reverse = signal.side == 'sell'
                sorted_targets_data = sorted(targets_data, reverse=sort_targets_reverse, key=lambda t: t['tp_price'])
                auto_target_share = round_down(1 / len(sorted_targets_data))
                for i in range(len(sorted_targets_data)):
                    target_data = targets_data[i]
                    share = round(1 - (len(sorted_targets_data) - 1) * auto_target_share, 2) if i == len(
                        sorted_targets_data) - 1 else auto_target_share
                    target = FuturesTarget(signal=signal,
                                           tp_price=target_data.get('tp_price'),
                                           share=share)
                    target.save()
                    targets.append(target)

            signal.targets.set(targets)
            signal.related_targets = targets

            new_bot = FuturesBot(exchange_id=exchange_id,
                                 credential_id=credential_id,
                                 strategy=strategy,
                                 position=position)
            if position.order_type == 'limit':
                new_bot.status = 'created'

            self.init_bot_requirements(bot=new_bot)
            strategy_developer = FuturesStrategyCenter.get_strategy_developer(strategy)
            new_bot.set_strategy_state_data(strategy_developer.init_strategy_state_data(position))
            new_bot.save()
            if credential_id in self._bots:
                self._bots[credential_id][new_bot.id] = new_bot
            else:
                self._bots[credential_id] = {new_bot.id: new_bot}

            return new_bot

    def reload_bots(self):
        bots = list(FuturesBot.objects.filter(is_active=True))
        for bot in bots:
            self.init_bot_requirements(bot)
            self.set_bot_strategy_state_data(bot)
            if bot.credential_id in self._bots:
                self._bots[bot.credential_id][bot.id] = bot
            else:
                self._bots[bot.credential_id] = {bot.id: bot}
        return bots

    def set_bot_strategy_state_data(self, bot):
        strategy_developer = FuturesStrategyCenter.get_strategy_developer(bot.strategy)
        bot.set_strategy_state_data(strategy_developer.reload_setup(bot.position))

    def get_public_client(self, exchange_id):
        if exchange_id in self._public_clients:
            public_client = self._public_clients[exchange_id]
        else:
            public_client = PublicClient(exchange_id=exchange_id)
            self._public_clients[exchange_id] = public_client
        return public_client

    def init_bot_requirements(self, bot):
        private_client = PrivateClient(exchange_id=bot.exchange_id, credential_id=bot.credential_id)
        public_client = self.get_public_client(exchange_id=bot.exchange_id)
        bot.init_requirements(private_client=private_client, public_client=public_client)
        bot.ready()

    def run_bots(self):
        while True:
            bots = self.reload_bots()
            for bot in bots:
                try:
                    if bot.status == FuturesBot.Status.RUNNING.value:
                        strategy_developer = FuturesStrategyCenter.get_strategy_developer(bot.strategy)
                        price_required_symbols = strategy_developer.get_strategy_symbols(bot.position)
                        symbol_prices = self._get_prices_if_available(bot.exchange_id, price_required_symbols)
                        t1 = time.time()
                        is_first_iteration = True
                        while not symbol_prices:
                            t2 = time.time()
                            delta_t = t2 - t1
                            if delta_t > 60 or is_first_iteration:
                                if is_first_iteration:
                                    is_first_iteration = False
                                else:
                                    t1 = time.time()
                                self._start_symbols_price_ticker(bot.exchange_id, price_required_symbols)
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
                        self._bots[bot.credential_id].pop(bot.id)

                    if not bot.status == FuturesBot.Status.RUNNING.value:
                        price_ticker = self._price_tickers[bot.position.signal.symbol]
                        price_ticker.unsubscribe_bot(bot.id)

                except Exception as e:
                    logger = my_get_logger()
                    logger.exception(e)
            time.sleep(1)

    def run_bots_limit_order_based(self):
        while True:
            credentials = list(self._bots.keys())
            active_bots = []
            for credential in credentials:
                active_bots += [bot for bot in list(self._bots[credential].values())]
            for bot in active_bots:
                position = bot.position
                signal = position.signal
                step = signal.related_steps[0]
                multiplier = 0.001
                size = int(((step.margin * signal.leverage) / step.entry_price) / multiplier) * multiplier
                if bot.status == FuturesBot.Status.CREATED.value:
                    bot._private_client.create_limit_order(
                        symbol=signal.symbol,
                        leverage=signal.leverage,
                        side=signal.trend,
                        size=size,
                        price=step.entry_price,
                        multiplier=multiplier
                    )

                    bot.status = FuturesBot.Status.WAITING.value
                    bot.save()
                else:
                    open_positions = bot._private_client.get_all_positions()
                    open_positions = open_positions if isinstance(open_positions, list) else []
                    for open_position in open_positions:
                        if open_position['symbol'] == with2without_slash_f(signal.symbol):
                            if bot.status == FuturesBot.Status.WAITING.value:
                                target = signal.related_targets[0]
                                stoploss = signal.stoploss
                                bot._private_client.create_limit_order(
                                    symbol=signal.symbol,
                                    leverage=signal.leverage,
                                    side='buy' if signal.trend == 'sell' else 'sell',
                                    size=size,
                                    price=target.tp_price,
                                    multiplier=multiplier
                                )
                                bot._private_client.create_stop_market_order(
                                    symbol=signal.symbol,
                                    leverage=signal.leverage,
                                    side='buy' if signal.trend == 'sell' else 'sell',
                                    size=size,
                                    multiplier=multiplier,
                                    stop='down' if signal.trend == 'buy' else 'up',
                                    stop_price=stoploss.trigger_price,
                                )

                                position.is_triggered = True
                                bot.is_active = False
                                bot.status = FuturesBot.Status.RUNNING.value
                                bot.save()
                            break
                    else:
                        if bot.status == FuturesBot.Status.RUNNING.value:
                            bot._private_client.cancel_all_stop_orders(symbol=signal.symbol)
                            bot._private_client.cancel_all_limit_orders(symbol=signal.symbol)
                            bot.status = FuturesBot.Status.STOPPED.value
                            self._bots[bot.credential_id].pop(bot.id)
                            bot.save()

            time.sleep(1)

    def _get_prices_if_available(self, exchange_id, symbols: List):
        symbol_prices = self._read_prices(exchange_id, symbols)
        for symbol in symbols:
            if not (symbol in symbol_prices and symbol_prices[symbol]):
                return

        return symbol_prices

    def _start_symbols_price_ticker(self, exchange_id, symbols: List):

        symbol_prices = self._read_prices(exchange_id, symbols)
        for symbol in symbols:
            if not (symbol in symbol_prices and symbol_prices[symbol]):
                if symbol in self._price_tickers:
                    price_ticker = self._price_tickers[symbol]
                    logger = my_get_logger()
                    logger.warning(
                        'Error in futures{} price ticker {} was occurred!'.format(
                            ' muck' if is_test else '', price_ticker.id))
                    price_ticker.stop()
                    # time.sleep(10) # maybe this is not required
                self._init_price_ticker(exchange_id, symbol)

    def _init_price_ticker(self, exchange_id, symbol):
        logger = my_get_logger()
        logger.info('price_ticker {} was started'.format(self.number_of_tickers))
        if False:
            args = self._start_muck_symbol_price_ticker(exchange_id, symbol)
        else:
            args = self._start_symbol_price_ticker(exchange_id, symbol)
        t = Thread(target=asyncio.run, args=(args,))
        self._price_tickers[symbol] = PriceTicker(self.number_of_tickers, t)
        t.start()
        self.number_of_tickers += 1

    async def _start_muck_symbol_price_ticker(self, exchange_id, symbol):
        uri = "ws://localhost:9000"
        cache_name = '{}_futures_price'.format(exchange_id)

        while True:
            price_ticker = self._price_tickers[symbol]
            try:
                async with websockets.connect(uri) as websocket:
                    client = websocket
                    price_ticker.client = websocket
                    loop = asyncio.get_event_loop()

                    def close_ws():
                        _logger = my_get_logger()
                        _logger.warning('websocket {} was closed'.format(price_ticker.id))
                        asyncio.ensure_future(client.close(), loop=loop)

                    price_ticker.stop = close_ws
                    await websocket.send(symbol)
                    while True:
                        try:
                            price = await websocket.recv()
                            CacheUtils.write_to_cache(symbol, float(price), cache_name)
                        except (ConnectionClosedError,) as e:
                            logger = my_get_logger()
                            logger.warning(e)
                            break
                    break
            except (OSError, ConnectionClosedError, TimeoutError):
                logger = my_get_logger()
                logger.warning('Could not connect to muck price server from price ticker {}!'.format(price_ticker.id))

    async def _start_symbol_price_ticker(self, exchange_id, symbol):
        cache_name = '{}_futures_price'.format(exchange_id)
        if exchange_id == 'kucoin':
            loop = asyncio.get_event_loop()
            ticker_topic = '/contractMarket/tickerV2:{}'.format(with2without_slash_f(symbol))

            async def deal_msg(msg):
                if msg['topic'] == ticker_topic:
                    price = (float(msg['data']['bestBidPrice']) + float(msg['data']['bestAskPrice'])) / 2
                    CacheUtils.write_to_cache(symbol, price, cache_name)

            client = WsToken()

            @async_retry_on_timeout(self._public_clients[exchange_id])
            async def create_kucoin_futures_ws_client():
                return await MyKucoinFuturesWsClient.create(loop, client, deal_msg, private=False)

            ws_client = await create_kucoin_futures_ws_client()
            price_ticker = self._price_tickers[symbol]
            price_ticker.client = ws_client

            def close_ws():
                _logger = my_get_logger()
                _logger.warning('websocket {} was closed'.format(price_ticker.id))
                try:
                    asyncio.run(ws_client.unsubscribe(ticker_topic))
                    ws_client.close_connection()
                except (ConnectionClosedOK, ConnectionClosedError):
                    _logger.warning('ConnectionClosedOK in price ticker {}'.format(price_ticker.id))

            price_ticker.stop = close_ws

            await ws_client.subscribe(ticker_topic)
            while True:
                await asyncio.sleep(60, loop=loop)

    def _read_prices(self, exchange_id, symbols):
        cache_name = '{}_futures_price'.format(exchange_id)
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

    def find_active_bot_id_by_symbol(self, credential_id, symbol):
        active_bots = self.get_bots(credential_id, is_active=True)
        for bot in active_bots:
            if bot.position.signal.symbol == symbol:
                return bot.id
        logger = my_get_logger()
        logger.error('No active bot with symbol {} was found for credential_id {}!'.format(symbol, credential_id))

    def get_bots(self, credential_id, is_active):
        if is_active:
            bots_dict: dict = self._bots.get(credential_id, {})
            bots = list(bots_dict.values())
        else:
            bots = FuturesBot.objects.filter(Q(credential_id=credential_id))
        for bot in bots:
            if bot.is_active:
                self.set_bot_strategy_state_data(bot)
        return bots

    def edit_position(self, credential_id, bot_id, new_position_data, raise_error=False):
        bot = self.get_active_bot(credential_id, bot_id)
        if not bot:
            message = 'No active bot with id {} was found for credential_id {}'.format(bot_id, credential_id)
            if raise_error:
                raise CustomException(message)
            else:
                logger = my_get_logger()
                logger.error(message)
        else:
            strategy_developer = FuturesStrategyCenter.get_strategy_developer(bot.strategy)

            edited_data = []
            new_signal_data = new_position_data.get('signal')
            if new_signal_data:
                new_steps_data = new_signal_data.get('steps')
                setup_mode = new_signal_data.get('setup_mode', 'auto')
                if new_steps_data:
                    steps_was_edited = self._run_strategy_developer_command(
                        bot,
                        strategy_developer,
                        'edit_steps',
                        new_steps_data,
                        setup_mode,
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
                        setup_mode,
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
            logger = my_get_logger()
            logger.error('No active bot with id {} was found for credential_id {}'.format(bot_id, credential_id))
        else:
            bot.status = FuturesBot.Status.STOPPED_MANUALLY.value
            bot.is_active = False
            bot.close_position(test=is_test)
            bot.save()
            return bot

    def get_number_of_risky_bots(self, credential_id):
        active_bots = self.get_bots(credential_id, is_active=True)
        return len([bot for bot in active_bots if bot.is_risky()])

    def validate_bot_data(self, exchange_id, credential_id, symbol):
        return all([self.validate_risky_bots_limit(credential_id),
                    self.validate_contract_symbol(exchange_id, symbol),
                    self.validate_duplicate_position(credential_id, symbol)])

    def validate_risky_bots_limit(self, credential_id):
        if not self.get_number_of_risky_bots(credential_id) < max_number_of_risky_bots:
            logger = my_get_logger()
            logger.error('Creating bot failed because of violating max number of risky bots!')
            return False
        return True

    def validate_contract_symbol(self, exchange_id, symbol):
        public_client = self.get_public_client(exchange_id)
        if symbol not in public_client.load_markets():
            logger = my_get_logger()
            logger.error('Creating bot failed because contract with symbol {} does not exists!'.format(symbol))
            return False
        return True

    def validate_duplicate_position(self, credential_id, symbol):
        active_bots = self.get_bots(credential_id, is_active=True)
        for bot in active_bots:
            if bot.position.signal.symbol == symbol:
                logger = my_get_logger()
                logger.error('Creating bot failed because position with symbol {} is duplicate!'.format(symbol))
                return False
        return True
