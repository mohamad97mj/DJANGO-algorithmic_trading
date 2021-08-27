MEMORY_MAX_ENTRIES = 1000000
DEFAULT_TIMOUT = 7

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default',
    },

    'binance_price': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'bp',
        'KEY_FUNCTION': "trader.utils.key_function.my_key_function",
        'OPTIONS': {
            'MAX_ENTRIES': MEMORY_MAX_ENTRIES,
        },
        'TIMEOUT': DEFAULT_TIMOUT,
    },
    'kucoin_price': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'kp',
        'KEY_FUNCTION': "trader.utils.key_function.my_key_function",
        'OPTIONS': {
            'MAX_ENTRIES': MEMORY_MAX_ENTRIES,
        },
        'TIMEOUT': DEFAULT_TIMOUT,
    }

}
