from binance.client import Client
import os

api_key = os.environ.get('TEST_API_KEY')  # test
api_secret = os.environ.get('TEST_SECRET_KEY')  # test
proxies = {
    'http': 'http://ck2.slike.vip:2087',
    'https': 'http://ck2.slike.vip:2087'
}

client = Client(api_key, api_secret, testnet=True
                # {'proxies': proxies}
                )
# client.API_URL = 'https://testnet.binance.vision/api'
