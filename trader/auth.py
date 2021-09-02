import os

spot_credentials = {
    'binance_main': {
        'api_key': os.environ.get('BINANCE_MAIN_API_KEY'),
        'secret': os.environ.get('BINANCE_MAIN_SECRET')
    },
    'binance_test': {
        'api_key': os.environ.get('BINANCE_TEST_API_KEY'),
        'secret': os.environ.get('BINANCE_TEST_SECRET')
    },
    'kucoin_main': {
        'api_key': os.environ.get('KUCOIN_MAIN_API_KEY'),
        'secret': os.environ.get('KUCOIN_MAIN_SECRET'),
        'password': os.environ.get('KUCOIN_MAIN_PASSWORD')
    },
    'kucoin_test': {
        'api_key': os.environ.get('KUCOIN_TEST_API_KEY'),
        'secret': os.environ.get('KUCOIN_TEST_SECRET'),
        'password': os.environ.get('KUCOIN_TEST_PASSWORD')
    },
}

futures_credentials = {
    'kucoin_main': {
        'api_key': os.environ.get('KUCOIN_FUTURES_MAIN_API_KEY'),
        'secret': os.environ.get('KUCOIN_FUTURES_MAIN_SECRET'),
        'password': os.environ.get('KUCOIN_FUTURES_MAIN_PASSWORD')
    },
    'kucoin_test': {
        'api_key': os.environ.get('KUCOIN_FUTURES_TEST_API_KEY'),
        'secret': os.environ.get('KUCOIN_FUTURES_TEST_SECRET'),
        'password': os.environ.get('KUCOIN_FUTURES_TEST_PASSWORD')
    }
}
