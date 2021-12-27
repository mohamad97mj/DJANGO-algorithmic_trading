import multiprocessing
from django.core.cache import caches
from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from ..services import FuturesBotTrader
from global_utils import catch_all_exceptions


class FuturesPriceMonitorView(APIView):

    @catch_all_exceptions(log_level='error', reraise=True)
    def get(self, request, cache_name, location, format=None):
        from django.core.cache.backends import locmem
        content = []
        keys = locmem._caches[location].copy().keys()
        cache = caches[cache_name]
        if cache:
            content = {key: cache.get(key) for key in keys}

        return Response({
            'count': len(content),
            'pid': multiprocessing.current_process().pid,
            'content': content
        })


class FuturesRiskyBotsView(APIView):
    renderer_classes = (renderers.JSONRenderer,)

    # permission_classes = [mypermissions.MyCustomIsAuthenticated]
    # @REQUEST_TIME.time()

    @catch_all_exceptions(reraise=True)
    def get(self, request, format=None):
        credential_id = request.query_params.get('credential_id', 'kucoin_test')
        number_of_risky_bots = FuturesBotTrader.get_number_of_risky_bots(credential_id)
        return Response(data={'number_of_risky_bots': number_of_risky_bots})
