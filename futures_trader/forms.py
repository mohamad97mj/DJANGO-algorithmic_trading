from django import forms
from django.contrib.admin import widgets

from fetch import symbols


# from bootstrap_datepicker_plus.widgets import DateTimePickerInput


class DatetimePicker(forms.DateTimeInput):
    input_type = 'datetime'


class FuturesTradeZoneCreateForm(forms.Form):
    symbol = forms.ChoiceField(widget=forms.Select({'class': 'form-select'}),
                               choices=zip(symbols, symbols))
    slope_type = forms.ChoiceField(widget=forms.Select({'class': 'form-select'}),
                                   choices=[('Flat', 'Flat'), ('Incline', 'Incline')])
    level_type = forms.ChoiceField(widget=forms.Select({'class': 'form-select'}),
                                   choices=[('Support', 'Support'), ('Resistance', 'Resistance')])
    point1_stoploss = forms.FloatField()
    point1_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    point1_time = forms.TimeField(widget=widgets.AdminTimeWidget(attrs={'type': 'time'}))
    point1_price = forms.FloatField()
    point2_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    point2_time = forms.TimeField(widget=widgets.AdminTimeWidget(attrs={'type': 'time'}), required=False)
    point2_price = forms.FloatField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        slope_type = cleaned_data.get('slope_type')
        point2_date = cleaned_data.get('point2_date')
        point2_time = cleaned_data.get('point2_time')
        point2_price = cleaned_data.get('point2_price')
        if slope_type == 'Incline':
            if not point2_date:
                self.add_error('point2_date', 'Point2 date is required!')
            if not point2_time:
                self.add_error('point2_time', 'Point2 time is required!')
            if not point2_price:
                self.add_error('point2_price', 'Point2 price is required!')
