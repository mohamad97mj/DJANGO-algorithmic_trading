from django.views import View
from django.shortcuts import render

from futures_trader.forms import FuturesTradeZoneCreateForm
from futures_trader.services import FuturesBotTrader


class FuturesTradeZoneCreateView(View):

    def get(self, request):
        trade_zone_create_form = FuturesTradeZoneCreateForm()
        contex = {
            'trade_zone_create_form': trade_zone_create_form
        }
        return render(request, template_name='futures_trader/trade_zone_create.html', context=contex)

    def post(self, request):
        data = request.POST
        trade_zone_create_form = FuturesTradeZoneCreateForm(data=data)
        contex = {'trade_zone_create_form': trade_zone_create_form}
        if trade_zone_create_form.is_valid():
            cleaned_data = trade_zone_create_form.cleaned_data
            FuturesBotTrader.create_trade_zone(
                symbol=cleaned_data.get('symbol'),
                slope_type=cleaned_data.get('slope_type'),
                level_type=cleaned_data.get('level_type'),
                point1_date=cleaned_data.get('point1_date'),
                point1_time=cleaned_data.get('point1_time'),
                point1_price=cleaned_data.get('point1_price'),
                point2_date=cleaned_data.get('point2_date'),
                point2_time=cleaned_data.get('point2_time'),
                point2_price=cleaned_data.get('point2_price'),
            )
        return render(request, template_name='futures_trader/trade_zone_create.html', context=contex)
