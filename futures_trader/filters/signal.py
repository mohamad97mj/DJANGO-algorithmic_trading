from django_filters import FilterSet, DateFilter, TimeFilter, ChoiceFilter
from django.forms import DateInput
from django.contrib.admin import widgets

from ..models import FuturesSignal
from fetch import symbols


class FuturesSignalFilter(FilterSet):

    symbol = ChoiceFilter(choices=zip(symbols, symbols))
    status = ChoiceFilter(choices=FuturesSignal.Status.choices)
    from_date = DateFilter(widget=DateInput(attrs={'type': 'date'}),
                           method='filter_from_date',
                           label='From date')
    from_time = TimeFilter(
        label='From time',
        required=False,
        widget=widgets.AdminTimeWidget(attrs={'type': 'time'}),
        method='filter_from_time',
    )

    to_date = DateFilter(widget=DateInput(attrs={'type': 'date'}),
                         method='filter_to_date',
                         label='To date')

    to_time = TimeFilter(
        label='To time',
        required=False,
        widget=widgets.AdminTimeWidget(attrs={'type': 'time'}),
        method='filter_to_time',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.initial['is_active'] = False

    @staticmethod
    def filter_from_date(queryset, name, value):
        if value:
            return queryset.filter(created_at__date__gte=value)
        return queryset

    @staticmethod
    def filter_from_time(queryset, name, value):
        if value:
            return queryset.filter(created_at__time__gte=value)
        return queryset

    @staticmethod
    def filter_to_date(queryset, name, value):
        if value:
            return queryset.filter(created_at__date__lte=value)
        return queryset

    @staticmethod
    def filter_to_time(queryset, name, value):
        if value:
            return queryset.filter(created_at__time__lte=value)
        return queryset

    class Meta:
        model = FuturesSignal
        fields = (
            'symbol',
            'status',
        )
