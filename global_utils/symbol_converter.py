def with2without_slash(symbol):
    splitted_symbol = symbol.split('/')
    base = splitted_symbol[0]
    quote = splitted_symbol[1]
    return '{}{}'.format(base, quote)


def without2with_slash(symbol, market):
    with_slash_symbols = list(market.keys)
    without2with_slash_mapper = {s.replace('/', ''): s for s in with_slash_symbols}
    return without2with_slash_mapper[symbol]


def slash2dash(symbol: str):
    return symbol.replace('/', '-')


def without2with_slash_f(symbol):
    symbol = symbol[:-1].replace('XBT', 'BTC')
    quotes = ['USD', 'USDT']
    for q in quotes:
        quote_index = symbol.find(q)
        if quote_index != -1:
            base = symbol[:quote_index]
            quote = symbol[quote_index:]
            return '{}/{}'.format(base, quote)


def with2without_slash_f(symbol: str):
    splitted_symbol = symbol.replace('BTC', 'XBT').split('/')
    base = splitted_symbol[0]
    quote = splitted_symbol[1] + 'M'
    return '{}{}'.format(base, quote)



