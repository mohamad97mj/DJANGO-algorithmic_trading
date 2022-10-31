from django_filters import FilterSet, DateFilter, TimeFilter, ChoiceFilter
from django.forms import DateInput
from django.contrib.admin import widgets

from ..models import FuturesSignal
from fetch import symbols


class FuturesTradeZoneFilter(FilterSet):
    pass
