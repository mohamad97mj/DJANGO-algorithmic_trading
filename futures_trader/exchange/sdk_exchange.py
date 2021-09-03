from kucoin_futures import client


class SdkExchange:
    def __init__(self, api_key, secret, password, is_sandbox):
        self.market_client = client.Market(is_sandbox=is_sandbox)
        self.trade_client = client.Trade(key=api_key,
                                         secret=secret,
                                         passphrase=password,
                                         is_sandbox=is_sandbox,)
        self.user_client = client.User(key=api_key, secret=secret, passphrase=password, is_sandbox=is_sandbox)


