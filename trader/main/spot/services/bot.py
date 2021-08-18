from ..models import SpotPosition, SpotBot
from ..trader import trader


class SpotPositionService():

    @staticmethod
    def get_bot(position_id: int):
        return SpotBot.objects.get(position_id=position_id)

    @staticmethod
    def open_position(exchange_id: str, credential_id: str, strategy: str, position: SpotPosition):
        return trader.open_position(exchange_id=exchange_id,
                                    credential_id=credential_id,
                                    strategy=strategy,
                                    position=position)

    @staticmethod
    def add_position_step(position_id, buy_price, share):
        return trader.add_position(position_id, buy_price, share)

    @staticmethod
    def edit_position(position_id, command, *args, **kwargs):
        return trader.edit_position(position_id, command, *args, **kwargs)
