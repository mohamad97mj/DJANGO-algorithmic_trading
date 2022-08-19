import json
from urllib.parse import urlencode

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.shortcuts import reverse, render, redirect
from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.views import FilterView


from ..services import FuturesBotTrader
from ..serializers import FuturesBotSerializer
from ..tables import FuturesBotTable
from ..filters import FuturesBotFilter
from global_utils import catch_all_exceptions


class FuturesBotsView(APIView):
    renderer_classes = (renderers.JSONRenderer,)

    # permission_classes = [mypermissions.MyCustomIsAuthenticated]
    # @REQUEST_TIME.time()

    @catch_all_exceptions()
    def get(self, request, format=None):
        credential_id = request.query_params.get('credential_id', 'kucoin_test')
        is_active = request.query_params.get('is_active', 'false') == 'true'
        bot_instances = FuturesBotTrader.get_bots(credential_id=credential_id, is_active=is_active)
        return Response(data=FuturesBotSerializer(bot_instances, many=True).data)

    @catch_all_exceptions()
    def post(self, request, format=None):
        """
        Opens a new position.
        """

        data = request.data
        bot_serializer = FuturesBotSerializer(data=data)

        bot_data = None
        if bot_serializer.is_valid():
            bot_instance = FuturesBotTrader.create_bot(bot_serializer.validated_data)
            bot_data = FuturesBotSerializer(instance=bot_instance).data

        return Response(bot_data)


class FuturesBotListView(SingleTableMixin, FilterView):
    table_class = FuturesBotTable
    filterset_class = FuturesBotFilter
    template_name = 'base/filter_table.html'


class FuturesBotActionView(APIView):
    def post(self, request, bot_id):
        data = request.data
        action = data.get('action')
        if action == 'stop':
            FuturesBotTrader.stop_bot('kucoin_main', bot_id)
        return redirect(reverse('futures_trader:futures_bot_list') + '?' + urlencode(request.query_params))


class FuturesBotDetailView(APIView):
    @catch_all_exceptions()
    def get(self, request, bot_id, format=None):
        credential_id = request.query_params.get('credential_id', 'kucoin_test')
        bot_instance = FuturesBotTrader.get_bot(credential_id=credential_id, bot_id=bot_id)
        return Response(data=FuturesBotSerializer(instance=bot_instance).data)

    @catch_all_exceptions()
    def put(self, request, bot_id, format=None):
        data = json.loads(request.body)
        command = data['command']
        credential_id = data.get('credential_id', 'kucoin_test')
        bot_instance = command_mapper[command](credential_id, bot_id)
        return Response(data=FuturesBotSerializer(instance=bot_instance).data)


command_mapper = {
    'pause': FuturesBotTrader.pause_bot,
    'start': FuturesBotTrader.start_bot,
    'stop': FuturesBotTrader.stop_bot,
}
