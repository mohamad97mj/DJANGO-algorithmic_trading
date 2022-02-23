MEMORY_MAX_ENTRIES = 1000000
DEFAULT_TIMEOUT = 7

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default',
    },

    'binance_spot_price': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'bsp',
        'KEY_FUNCTION': "global_utils.my_key_function",
        'OPTIONS': {
            'MAX_ENTRIES': MEMORY_MAX_ENTRIES,
        },
        'TIMEOUT': DEFAULT_TIMEOUT,
    },
    'binance_futures_price': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'bfp',
        'KEY_FUNCTION': "global_utils.my_key_function",
        'OPTIONS': {
            'MAX_ENTRIES': MEMORY_MAX_ENTRIES,
        },
        'TIMEOUT': DEFAULT_TIMEOUT,
    },
    'kucoin_spot_price': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ksp',
        'KEY_FUNCTION': "global_utils.my_key_function",
        'OPTIONS': {
            'MAX_ENTRIES': MEMORY_MAX_ENTRIES,
        },
        'TIMEOUT': DEFAULT_TIMEOUT,
    },

    'kucoin_futures_price': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'kfp',
        'KEY_FUNCTION': "global_utils.my_key_function",
        'OPTIONS': {
            'MAX_ENTRIES': MEMORY_MAX_ENTRIES,
        },
        'TIMEOUT': DEFAULT_TIMEOUT,
    }

}
