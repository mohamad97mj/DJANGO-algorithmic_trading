import ccxt.async_support as ccxt

# enable built-in rate limiting upon instantiation of the exchange
exchange = ccxt.bitfinex({
    'enableRateLimit': True,
})

# or switch the built-in rate-limiter on or off later after instantiation
exchange.enableRateLimit = True  # enable
exchange.enableRateLimit = False  # disable


class ExchageFactory:
    def create_exchange(self, name='binance'):
        exchange = getattr(ccxt, name)({
            'enableRateLimit': True,
        })
        return exchange
