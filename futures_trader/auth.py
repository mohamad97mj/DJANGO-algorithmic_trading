import os

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
