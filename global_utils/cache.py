from django.core.cache import caches
from django.conf import settings


class CacheUtils:
    default_timeout = settings.DEFAULT_TIMOUT

    @staticmethod
    def read_from_cache(key, cache_name):
        cache = caches[cache_name]
        return cache.get(key)

    @staticmethod
    def write_to_cache(key, value, cache_name, timeout=default_timeout):
        cache = caches[cache_name]
        cache.set(key, value, timeout=timeout)
