from ..models import SpotPosition, SpotBot
from ..trader import trader
from django.db.models import Q


class SpotBotService():

    @staticmethod
    def create_bot(bot_data: dict):
        return trader.create_bot(exchange_id=bot_data['exchange_id'],
                                 credential_id=bot_data['credential_id'],
                                 strategy=bot_data['strategy'],
                                 position_data=bot_data['position'])

    @staticmethod
    def edit_position_steps(bot_id, new_steps, step_share_set_mode):
        return trader.edit_none_triggered_steps(bot_id, new_steps, step_share_set_mode)
