def with2without_slash(symbol):
    splitted_symbol = symbol.split('/')
    base = splitted_symbol[0]
    quote = splitted_symbol[1]
    return '{}{}'.format(base, quote)


def without2with_slash(symbol, market):
    with_slash_symbols = list(market.keys)
    pass