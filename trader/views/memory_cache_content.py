import multiprocessing
from rest_framework.views import APIView
from rest_framework.response import Response
from global_utils import catch_all_exceptions
from django.core.cache import caches


class MemoryCacheContentView(APIView):

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
