# import os
# from pprint import pprint
# from binance.client import Client
# from binance.websockets import BinanceSocketManager
# from twisted.internet import reactor
# api_key = 'knBxiPJqJhGwpADVP4sqvH8RXLnc8vBPIB1iTKDONQ07q2VD9Ik7KCmqxCw1rrMT'  # test
# api_key = 'm6IcuuOFD4r1OiS5Mw87UjNjiKPav14CviOOyxz6CvG17AY1QBIxuPF7v6scDuqg' #main
# api_secret = '4Pf1cmFJ7qi5aefurLjQSIvb3iGCDcEnkgPi4qvlDSulcFQlbQZgIGTgHcUJgvDG'  # test
# api_secret = 'B0CdJ9l95FOdtsZPdZ4oNRhnqj2mor7EniB99icmrxUW8bt5eoRZhk8CVCRfQau5' #main
# client = Client(api_key, api_secret)
# client.API_URL = 'https://testnet.binance.vision/api'
# pprint(client.get_account())
# pprint(client.get_asset_balance(asset='BTC'))
# get latest price from Binance API
# btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
# print full output (dictionary)
# print(btc_price)
# btc_price = {'error': False}
# def btc_trade_history(msg):
#     """ define how to process incoming WebSocket messages """
#     if msg['e'] != 'error':
#         print(msg['c'])
#         btc_price['last'] = msg['c']
#         btc_price['bid'] = msg['b']
#         btc_price['last'] = msg['a']
#     else:
#         btc_price['error'] = True

# init and start the WebSocket
# bsm = BinanceSocketManager(client)
# conn_key = bsm.start_symbol_ticker_socket('BTCUSDT', btc_trade_history)
# bsm.start()
# print(help(BinanceSocketManager))


import sys
import os
import functools
import logging

logging.basicConfig(level=logging.INFO)


def log_decorator(_func=None):
    def log_decorator_info(func):
        @functools.wraps(func)
        def log_decorator_wrapper(*args, **kwargs):

            """log function begining"""
            # logging.info("Begin function {}".format(func.__name__))
            print('--Begin function {} - args:{}, kwargs:{}'.format(func.__name__, args, kwargs))
            try:
                """ log return value from the function """
                value = func(*args, **kwargs)
                # logging.info(f"Returned: - End function {value!r}")
                print('--End function {} - returned value: '.format(func.__name__, value))
            except:
                """log exception if occurs in function"""
                logging.error(f"--Exception: {str(sys.exc_info()[1])}")
                raise
            return value

        return log_decorator_wrapper

    if _func is None:
        return log_decorator_info
    else:
        return log_decorator_info(_func)


@log_decorator
def add_test(a, b):
    print("hello, i am add")
    return a + b


add_test(2, 3)
