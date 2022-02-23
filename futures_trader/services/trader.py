from futures_trader.services.bot_handler import FuturesBotHandler
from global_utils.custom_exception import CustomException

bot_handler = FuturesBotHandler()


class FuturesBotTrader:

    @staticmethod
    def start_trading():
        bot_handler.reload_bots()
        bot_handler.run_bots_limit_order_based()

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
    def stop_bot(credential_id, bot_id):
        return bot_handler.stop_bot(credential_id, bot_id)
