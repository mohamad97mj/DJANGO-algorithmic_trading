from ..models import SpotPosition, SpotBot
from ..trader import trader
from django.db.models import Q


class SpotBotService():

    @staticmethod
    def get_bot(bot_id: int):
        return trader.get_bot(bot_id)

    @staticmethod
    def get_active_bots(credential_id):
        return SpotBot.objects.filter(Q(credential_id=credential_id) & Q(is_active=True))

    @staticmethod
    def create_bot(bot_data: dict):
        return trader.create_bot(exchange_id=bot_data['exchange_id'],
                                 credential_id=bot_data['credential_id'],
                                 strategy=bot_data['strategy'],
                                 position_data=bot_data['position'])

    @staticmethod
    def edit_position(bot_id, new_position_data):
        return trader.edit_position(bot_id, new_position_data, )
