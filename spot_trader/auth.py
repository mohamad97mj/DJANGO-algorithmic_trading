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
        'api_key': os.environ.get('KUCOIN_MAIN_API_KEY', '61272984300d59000665294e'),
        'secret': os.environ.get('KUCOIN_MAIN_SECRET', '4d48f02d-9e63-4cff-8eb9-e398c72b48a3'),
        'password': os.environ.get('KUCOIN_MAIN_PASSWORD', 'mJ604998')
    },
    'kucoin_test': {
        'api_key': os.environ.get('KUCOIN_TEST_API_KEY'),
        'secret': os.environ.get('KUCOIN_TEST_SECRET'),
        'password': os.environ.get('KUCOIN_TEST_PASSWORD')
    },
}

