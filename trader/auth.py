import os

credentials = {
    'main': {
        'api_key': os.environ.get('MAIN_API_KEY'),
        'secret_key': os.environ.get('MAIN_SECRET_KEY')
    },
    'test': {
        'api_key': os.environ.get('TEST_API_KEY'),
        'secret_key': os.environ.get('TEST_SECRET_KEY')
    }
}
