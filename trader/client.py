from binance.client import Client, AsyncClient
import os

api_key = os.environ.get('MAIN_API_KEY')  # test
# api_key = ''  # test
api_secret = os.environ.get('MAIN_SECRET_KEY')  # test
# api_secret = '' # test
proxies = {
    'http': 'http://ck2.slike.vip:2087',
    'https': 'http://ck2.slike.vip:2087'
}

client = Client(api_key, api_secret, testnet=True
                # {'proxies': proxies}
                )
# client.API_URL = 'https://testnet.binance.vision/api'
