import time
import os
from binance import ThreadedWebsocketManager

api_key = os.environ.get('MAIN_API_KEY')
api_secret = os.environ.get('MAIN_SECRET_KEY')
print(api_key)
print(api_secret)


def main():
    symbol = 'BTCUSDT'

    twm = ThreadedWebsocketManager()
    # start is required to initialise its internal loop
    twm.start()

    def handle_socket_message(msg):
        print(msg)

    twm.start_symbol_ticker_socket(callback=handle_socket_message, symbol='SUSHIUPUSDT')
    twm.start_symbol_ticker_socket(callback=handle_socket_message, symbol='ETHUSDT')

    # twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)
    # multiple sockets can be started
    # twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    # or a multiplex socket can be started like this
    # see Binance docs for stream names
    # streams = ['bnbbtc@miniTicker', 'bnbbtc@bookTicker']
    # twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)
    print("helooooooooooooooooooooooooooo")
    # twm.join()
    print('goodbyeeeeeeeeeeeeeeeeeeeeeeeee')


main()
