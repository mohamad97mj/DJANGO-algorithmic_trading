import datetime
from django.db import models
from django.utils import timezone


class FuturesTradeZone(models.Model):
    symbol = models.CharField(max_length=15)
    is_major = models.BooleanField(default=False)
    point1_datetime = models.DateTimeField()
    point1_price = models.FloatField()
    is_valid = models.BooleanField(default=True)

    def get_price(self, date_time=None):
        raise NotImplementedError

    class Meta:
        abstract = True


class FuturesFlatTradeZone(FuturesTradeZone):
    def get_price(self, date_time=None):
        return self.point1_price

    class Meta:
        abstract = True


class FuturesFlatSupportTradeZone(FuturesFlatTradeZone):
    pass


class FuturesFlatResistanceTradeZone(FuturesFlatTradeZone):
    pass


class FuturesInclineTradeZone(FuturesTradeZone):
    point2_datetime = models.DateTimeField()
    point2_price = models.FloatField()
    slope = models.FloatField(blank=True)

    def __init__(self, *args, **kwargs):
        super(FuturesInclineTradeZone, self).__init__(*args, **kwargs)
        self.slope = (self.point2_price - self.point1_price) / (
                self.point2_datetime.timestamp() - self.point1_datetime.timestamp())

    def get_price(self, date_time: datetime = None):
        timestamp = (date_time or datetime.datetime.now()).timestamp()
        point1_timestamp = self.point1_datetime.timestamp()
        price = self.point1_price + self.slope * (timestamp - point1_timestamp)
        return price

    class Meta:
        abstract = True


class FuturesInclineSupportTradeZone(FuturesInclineTradeZone):
    pass


class FuturesInclineResistanceTradeZone(FuturesInclineTradeZone):
    pass


def get_closest_zone_price(symbol, price, level_type, date_time, is_major=False):
    filter_kwargs = {}
    if is_major:
        filter_kwargs.update({
            is_major: True
        })

    if level_type == 'support':
        valid_major_flat_support_trade_zones = list(
            FuturesFlatSupportTradeZone.objects.filter(symbol=symbol, point1_price__lte=price, is_valid=True,
                                                       **filter_kwargs))
        valid_major_incline_support_trade_zones = list(
            FuturesInclineSupportTradeZone.objects.filter(symbol=symbol, point1_price__lte=price, is_valid=True,
                                                          **filter_kwargs))
        closest_zone_price = 0
        for zone in valid_major_flat_support_trade_zones + valid_major_incline_support_trade_zones:
            zone_price = zone.get_price(date_time=date_time)
            if zone_price > closest_zone_price:
                closest_zone_price = zone_price
        return closest_zone_price
    else:
        valid_major_flat_resistant_trade_zones = list(
            FuturesFlatResistanceTradeZone.objects.filter(symbol=symbol, point1_price__gte=price, is_valid=True,
                                                          **filter_kwargs))
        valid_major_incline_resistant_trade_zones = list(
            FuturesInclineResistanceTradeZone.objects.filter(symbol=symbol, point1_price__gte=price,
                                                             is_valid=True, **filter_kwargs))
        closest_zone_price = 1000000
        for zone in valid_major_flat_resistant_trade_zones + valid_major_incline_resistant_trade_zones:
            zone_price = zone.get_price(date_time=date_time)
            if zone_price < closest_zone_price:
                closest_zone_price = zone_price
        return closest_zone_price


def has_price_action_confirmation(signal_side, price, date_time=None):
    date_time = date_time or datetime.datetime.now()
    if signal_side == 'buy':
        closest_support_zone_price = get_closest_zone_price(symbol=symbol, price=price, level_type='support',
                                                            date_time=date_time)
        closest_major_resistance_zone_price = get_closest_zone_price(symbol=symbol, price=price,
                                                                     level_type='resistance', date_time=date_time,
                                                                     is_major=True)
        risk = price - closest_support_zone_price
        reward = closest_major_resistance_zone_price - price

    else:
        closest_resistance_zone_price = get_closest_zone_price(symbol=symbol, price=price, level_type='resistance',
                                                               date_time=date_time)
        closest_major_support_zone_price = get_closest_zone_price(symbol=symbol, price=price, level_type='support',
                                                                  date_time=date_time, is_major=True)
        risk = closest_resistance_zone_price - price
        reward = price - closest_major_support_zone_price

    if 0 < risk / reward < 1 / 1.5:
        return True
    else:
        return False
