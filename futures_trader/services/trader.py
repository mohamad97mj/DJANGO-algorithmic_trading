import datetime

from futures_trader.services.bot_handler import FuturesBotHandler
from futures_trader.models.trade_zone import FuturesInclineSupportTradeZone, FuturesInclineResistanceTradeZone, \
    FuturesFlatSupportTradeZone, FuturesFlatResistanceTradeZone
from global_utils.custom_exception import CustomException

bot_handler = FuturesBotHandler()


class FuturesBotTrader:

    @staticmethod
    def start_trading():
        bot_handler.run_bots_semi_limit_order_based()

    @staticmethod
    def get_bot(credential_id: str, bot_id: str):
        return bot_handler.get_bot(credential_id, bot_id)

    @staticmethod
    def get_bots(credential_id, is_active):
        return bot_handler.get_bots(credential_id, is_active)

    @staticmethod
    def get_number_of_risky_bots(credential_id):
        return bot_handler.get_number_of_risky_bots(credential_id)

    @staticmethod
    def create_bot(bot_data: dict):
        return bot_handler.create_bot(exchange_id=bot_data['exchange_id'],
                                      credential_id=bot_data['credential_id'],
                                      strategy=bot_data['strategy'],
                                      position_data=bot_data['position'])

    @staticmethod
    def edit_position(credential_id, new_position_data, bot_id=None, symbol=None, raise_error=False):
        if not bot_id:
            if not symbol:
                raise CustomException('bot_id or symbol is required to edit position!')
            else:
                bot_id = bot_handler.find_active_bot_id_by_symbol(credential_id, symbol)
        if bot_id:
            return bot_handler.edit_position(credential_id, bot_id, new_position_data, raise_error=raise_error)

    @staticmethod
    def pause_bot(credential_id, bot_id):
        return bot_handler.pause_bot(credential_id, bot_id)

    @staticmethod
    def start_bot(credential_id, bot_id):
        return bot_handler.start_bot(credential_id, bot_id)

    @staticmethod
    def stop_bot(credential_id, bot_id=None, symbol=None):
        if not bot_id:
            if not symbol:
                raise CustomException('bot_id or symbol is required to stop bot!')
            else:
                bot_id = bot_handler.find_active_bot_id_by_symbol(credential_id, symbol)
        if bot_id:
            return bot_handler.stop_bot(credential_id, bot_id)

    @staticmethod
    def create_trade_zone(symbol, slope_type, level_type, point1_stoploss, point1_date, point1_time, point1_price,
                          point2_date=None, point2_time=None, point2_price=None):
        tz_class = {
            'FlatSupport': FuturesFlatSupportTradeZone,
            'FlatResistance': FuturesFlatResistanceTradeZone,
            'InclineSupport': FuturesInclineSupportTradeZone,
            'InclineResistance': FuturesInclineResistanceTradeZone,
        }[slope_type + level_type]
        kwargs = {}
        if slope_type == 'Incline':
            kwargs['point2_datetime'] = datetime.datetime(year=point2_date.year,
                                                          month=point2_date.month,
                                                          day=point2_date.day,
                                                          hour=point2_time.hour,
                                                          minute=point2_time.minute,
                                                          second=point2_time.second)
            kwargs['point2_price'] = point2_price
        tz_class.objects.create(symbol=symbol,
                                point1_stoploss=point1_stoploss,
                                point1_datetime=datetime.datetime(year=point1_date.year,
                                                                  month=point1_date.month,
                                                                  day=point1_date.day,
                                                                  hour=point1_time.hour,
                                                                  minute=point1_time.minute,
                                                                  second=point1_time.second),
                                point1_price=point1_price,
                                **kwargs)
