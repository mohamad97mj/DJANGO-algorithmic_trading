import os

credentials = {
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
        'secret': os.environ.get('KUCOIN_MAIN_SECRET')
    },
    'kucoin_test': {
        'api_key': os.environ.get('KUCOIN_TEST_API_KEY'),
        'secret': os.environ.get('KUCOIN_TEST_SECRET')
    }
}
