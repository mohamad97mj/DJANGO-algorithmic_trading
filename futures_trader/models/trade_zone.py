import datetime
from django.db import models
from django.utils import timezone


class FuturesTradeZone(models.Model):
    symbol = models.CharField(max_length=15)
    point1_stoploss = models.FloatField()
    point1_datetime = models.DateTimeField()
    point1_price = models.FloatField()
    is_valid = models.BooleanField(default=True)

    # point1_upper_price = models.FloatField()
    # point1_lower_price = models.FloatField()

    def get_point_stoploss(self, date_time=None):
        raise NotImplementedError

    def get_point_price(self, date_time=None):
        raise NotImplementedError

    class Meta:
        abstract = True


class FuturesFlatTradeZone(FuturesTradeZone):
    def get_point_stoploss(self, date_time=None):
        return self.point1_stoploss

    class Meta:
        abstract = True


class FuturesFlatSupportTradeZone(FuturesFlatTradeZone):
    pass


class FuturesFlatResistanceTradeZone(FuturesFlatTradeZone):
    pass


class FuturesInclineTradeZone(FuturesTradeZone):
    point2_datetime = models.DateTimeField()
    point2_price = models.FloatField()
    # point2_upper_price = models.FloatField()
    slope = models.FloatField(blank=True)

    def __init__(self, *args, **kwargs):
        super(FuturesInclineTradeZone, self).__init__(*args, **kwargs)
        self.slope = (self.point2_price - self.point1_price) / (
                self.point2_datetime.timestamp() - self.point1_datetime.timestamp())

    def get_point_stoploss(self, date_time: datetime = None):
        timestamp = (date_time or datetime.datetime.now()).timestamp()
        point1_timestamp = self.point1_datetime.timestamp()
        stoploss = self.point1_stoploss + self.slope * (timestamp - point1_timestamp)
        return stoploss

    def get_point_price(self, date_time: datetime = None):
        timestamp = (date_time or datetime.datetime.now()).timestamp()
        point1_timestamp = self.point1_datetime.timestamp()
        point_price = self.point1_price + self.slope * (timestamp - point1_timestamp)
        return point_price

    class Meta:
        abstract = True


class FuturesInclineSupportTradeZone(FuturesInclineTradeZone):
    pass


class FuturesInclineResistanceTradeZone(FuturesInclineTradeZone):
    pass


def get_closest_point_stoploss(symbol, current_price, level_type, date_time=None):
    date_time = date_time or datetime.datetime.now()
    if level_type == 'support':
        valid_flat_support_trade_zones = list(
            FuturesFlatTradeZone.objects.filter(symbol=symbol, point1_stoploss__lte=current_price, is_valid=True))
        valid_incline_support_trade_zones = list(
            FuturesInclineSupportTradeZone.objects.filter(symbol=symbol,
                                                          point1_stoploss__lte=current_price, is_valid=True))
        closest_stoploss = 0
        for zone in valid_flat_support_trade_zones + valid_incline_support_trade_zones:
            zone_stoploss = zone.get_point_stoploss(date_time=date_time)
            if zone_stoploss > closest_stoploss:
                closest_stoploss = zone_stoploss
        return closest_stoploss
    else:
        valid_flat_resistant_trade_zones = list(
            FuturesFlatTradeZone.objects.filter(symbol=symbol, point1_stoploss__lte=current_price, is_valid=True))
        valid_incline_resistant_trade_zones = list(
            FuturesInclineSupportTradeZone.objects.filter(symbol=symbol,
                                                          point1_stoploss__lte=current_price, is_valid=True))
        closest_stoploss = 0
        for zone in valid_flat_resistant_trade_zones + valid_incline_resistant_trade_zones:
            zone_stoploss = zone.get_point_stoploss(date_time=date_time)
            if zone_stoploss > closest_stoploss:
                closest_stoploss = zone_stoploss
        return closest_stoploss

def get_closest_point_price():
    pass
