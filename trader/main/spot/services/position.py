from ..models import SpotPosition
from ..trader import trader


class SpotPositionService():

    @staticmethod
    def open_position(exchange_id: str, credential_id: str, position: SpotPosition):
        trader.open_position(exchange_id=exchange_id, credential_id=credential_id, position=position)
