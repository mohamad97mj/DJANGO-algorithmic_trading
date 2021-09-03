from kucoin import client


class SdkExchange:
    def __init__(self, api_key, secret, password, is_sandbox):
        url = 'https://openapi-sandbox.kucoin.com' if is_sandbox else 'https://api.kucoin.com'
        self.market_client = client.Market(url=url)
        self.trade_client = client.Trade(key=api_key,
                                         secret=secret,
                                         passphrase=password,
                                         is_sandbox=is_sandbox,
                                         url=url)
        self.user_client = client.User(key=api_key, secret=secret, passphrase=password, is_sandbox=is_sandbox)
