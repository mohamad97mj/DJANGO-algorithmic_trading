import os

futures_credentials = {
    'kucoin_main': {
        'api_key': os.environ.get('KUCOIN_FUTURES_MAIN_API_KEY', '612f3c39d0d4e100068f297a'),
        'secret': os.environ.get('KUCOIN_FUTURES_MAIN_SECRET', '0db7f3fe-2d09-4c27-90b0-661cae4eeb81'),
        'password': os.environ.get('KUCOIN_FUTURES_MAIN_PASSWORD', 'mJ604998')
    },
    'kucoin_test': {
        'api_key': os.environ.get('KUCOIN_FUTURES_TEST_API_KEY'),
        'secret': os.environ.get('KUCOIN_FUTURES_TEST_SECRET'),
        'password': os.environ.get('KUCOIN_FUTURES_TEST_PASSWORD')
    }
}
