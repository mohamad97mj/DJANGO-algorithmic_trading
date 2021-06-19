from trader.spot.trader import trader


class SpotPositionService():

    @staticmethod
    def open_position():
        trader.open_position()
