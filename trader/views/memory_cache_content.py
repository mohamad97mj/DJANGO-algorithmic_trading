import os
import multiprocessing
from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from djangorestframework_camel_case import render
from video_api.global_utils import catch_all_exceptions


class MemoryCacheContentView(APIView):
    renderer_classes = (
        render.CamelCaseJSONRenderer,
        renderers.BrowsableAPIRenderer,
    ) if settings.DEBUG else (
        render.CamelCaseJSONRenderer,
        renderers.JSONRenderer,
    )

    @catch_all_exceptions(log_level='error', reraise=True)
    def get(self, request, cache_name, format=None):
        from django.core.cache.backends import locmem
        content = []
        cache = locmem._caches.get(cache_name, None)
        if cache:
            cache = cache.copy()
            content = cache.keys()

        return Response({
            'count': len(content),
            'pid': multiprocessing.current_process().pid,
            'content': content
        })
