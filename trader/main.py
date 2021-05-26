from trader.bots import SpotTrader
from trader.clients import PublicClient
from trader.exchange import ExchageFactory, Exchange


def main():
    # public_client = PublicClient()
    # print('exchanges are:', public_client.get_exchanges())
    exchange = ExchageFactory.create_exchange(exchange_id='binance')
    public_client = PublicClient(exchange=exchange)
    print(public_client.get_markets())


if __name__ == "__main__":
    main()
