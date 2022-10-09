from urllib.parse import urlencode

from django.shortcuts import reverse, render, redirect
from rest_framework.views import APIView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from ..services.trader import FuturesBotTrader
from ..clients import PublicClient
from ..models import FuturesSignal
from ..tables import FuturesSignalTable
from ..filters import FuturesSignalFilter
from ..config import LOSS_PERCENT, MAX_LEVERAGE, POSITION_MARGIN


class FuturesSignalListView(SingleTableMixin, FilterView):
    table_class = FuturesSignalTable
    filterset_class = FuturesSignalFilter
    template_name = 'base/filter_table.html'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['loss_percent'] = LOSS_PERCENT
        contex['margin'] = POSITION_MARGIN
        return contex


class FuturesSignalActionView(APIView):
    def post(self, request, signal_id):
        data = request.data
        action = data.get('action')
        if action == 'reject':
            FuturesSignal.objects.filter(id=signal_id).update(status='rejected')
        elif action == 'unreject':
            FuturesSignal.objects.filter(id=signal_id).update(status='waiting')
        elif action == 'confirm':
            signal = FuturesSignal.objects.get(id=signal_id)
            step = PublicClient().fetch_ticker(signal.symbol)
            stoploss = float(data.get('stoploss'))
            risk = abs(step - stoploss) / step
            loss_percent = float(data.get('loss_percent'))
            leverage = min(int(loss_percent / (100 * risk)), MAX_LEVERAGE)
            signal.leverage = leverage
            target1 = float(data.get('target1'))
            target2 = float(data.get('target2'))
            margin = float(data.get('margin'))
            signal_data = {'obj': signal,
                           'steps': [{'entry_price': -1, }],
                           'targets': [{'tp_price': target1}, {'tp_price': target2}],
                           'stoploss': {'trigger_price': stoploss}}
            position_data = {
                'signal': signal_data,
                'margin': margin,
            }
            bot_data = {
                'exchange_id': 'kucoin',
                'credential_id': 'kucoin_main',
                'strategy': 'manual',
                'position': position_data,
            }
            FuturesBotTrader.create_bot(bot_data)
            signal.status = 'confirmed'
            signal.save()
        return redirect(reverse('futures_trader:futures_signal_list') + '?' + urlencode(request.query_params))
