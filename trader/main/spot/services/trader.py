from ..bot_handler import SpotBotHandler

bot_handler = SpotBotHandler()


class SpotBotTrader:

    @staticmethod
    def start_trading():
        bot_handler.reload_bots()
        bot_handler.run_bots()

    @staticmethod
    def get_bot(bot_id: str, credential_id: str):
        return bot_handler.get_bot(bot_id, credential_id)

    @staticmethod
    def get_bots(credential_id, is_active):
        return bot_handler.get_bots(credential_id, is_active)

    @staticmethod
    def create_bot(bot_data: dict):
        return bot_handler.create_bot(exchange_id=bot_data['exchange_id'],
                                      credential_id=bot_data['credential_id'],
                                      strategy=bot_data['strategy'],
                                      position_data=bot_data['position'])

    @staticmethod
    def edit_position(bot_id, new_position_data):
        return bot_handler.edit_position(bot_id, new_position_data, )

    @staticmethod
    def pause_bot(bot_id):
        return bot_handler.pause_bot(bot_id)

    @staticmethod
    def start_bot(bot_id):
        return bot_handler.start_bot(bot_id)

    @staticmethod
    def stop_bot(blot_id):
        pass
