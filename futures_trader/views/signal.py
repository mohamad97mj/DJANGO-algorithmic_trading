from django.shortcuts import reverse, render, redirect
from rest_framework.views import APIView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from ..models import FuturesSignal
from ..tables import FuturesSignalTable
from ..filters import FuturesSignalFilter


class FuturesSignalListView(SingleTableMixin, FilterView):
    table_class = FuturesSignalTable
    filterset_class = FuturesSignalFilter
    template_name = 'base/filter_table.html'


class FuturesSignalActionView(APIView):
    def post(self, request, signal_id):
        data = request.data
        action = data.get('action')
        if action == 'reject':
            FuturesSignal.objects.filter(id=signal_id).update(status='rejected')
        elif action == 'unreject':
            FuturesSignal.objects.filter(id=signal_id).update(status='waiting')
        return redirect(reverse('futures_trader:futures_signal_list'))
