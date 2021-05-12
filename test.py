import os
from pprint import pprint
from binance.client import Client
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

api_key = 'knBxiPJqJhGwpADVP4sqvH8RXLnc8vBPIB1iTKDONQ07q2VD9Ik7KCmqxCw1rrMT'  # test
# api_key = 'm6IcuuOFD4r1OiS5Mw87UjNjiKPav14CviOOyxz6CvG17AY1QBIxuPF7v6scDuqg' #main
api_secret = '4Pf1cmFJ7qi5aefurLjQSIvb3iGCDcEnkgPi4qvlDSulcFQlbQZgIGTgHcUJgvDG'  # test
# api_secret = 'B0CdJ9l95FOdtsZPdZ4oNRhnqj2mor7EniB99icmrxUW8bt5eoRZhk8CVCRfQau5' #main
client = Client(api_key, api_secret)
client.API_URL = 'https://testnet.binance.vision/api'
#
pprint(client.get_account())

pprint(client.get_asset_balance(asset='BTC'))

# get latest price from Binance API
btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
# print full output (dictionary)
print(btc_price)

btc_price = {'error': False}


def btc_trade_history(msg):
    """ define how to process incoming WebSocket messages """
    if msg['e'] != 'error':
        print(msg['c'])
        btc_price['last'] = msg['c']
        btc_price['bid'] = msg['b']
        btc_price['last'] = msg['a']
    else:
        btc_price['error'] = True


# init and start the WebSocket
bsm = BinanceSocketManager(client)
conn_key = bsm.start_symbol_ticker_socket('BTCUSDT', btc_trade_history)
bsm.start()
# print(help(BinanceSocketManager))
