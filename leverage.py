def get_leverage(stoploss, price):
    return 10 / (100 * abs(price - stoploss) / price)



