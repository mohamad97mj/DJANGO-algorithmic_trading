from spot_trader.clients.public_client import PublicClient

symbols = [
    'TRX/USDT',
    'BTC/USDT',
    'ETH/USDT',
    'BCH/USDT',
    'LINK/USDT',
    'UNI/USDT',
    'LTC/USDT',
    '1INCH/USDT',
    'DASH/USDT',
    'AAVE/USDT',
    'DOGE/USDT',
    'LUNA/USDT',
    'VET/USDT',
    'BNB/USDT',
    'SOL/USDT',
    'ALGO/USDT',
    'FTM/USDT',
    'MATIC/USDT',
    'THETA/USDT',
    'CHZ/USDT',
    'MANA/USDT',
    'NEO/USDT',
    'AXS/USDT',
    'EGLD/USDT',
    'NEAR/USDT',
    'ONE/USDT',
    'FLOW/USDT',
    'CELO/USDT',
    'ROSE/USDT',
    'ADA/USDT',
    'ATOM/USDT',
    'AVAX/USDT',
    'DOT/USDT',
    'SAND/USDT',
    'APE/USDT',
    'HBAR/USDT',
    'CRO/USDT',
    'CRV/USDT',
    'LRC/USDT',
    'KSM/USDT',
    'COMP/USDT',
    'BAT/USDT',
    'ICP/USDT',
    'MKR/USDT',
    'WAVES/USDT',
    'ENJ/USDT',
    'ETC/USDT',
    'ZEC/USDT',
    'XLM/USDT',
    'FIL/USDT',
    'GRT/USDT',
    'EOS/USDT',
    'SUSHI/USDT',
]


def save_ohlc_data():
    pb = PublicClient()
    for symbol in symbols:
        data = pb.fetch_ohlcv(
            symbol=symbol,
            timeframe='1h',
            limit=80,
        )
        f = open("data/ohlcv/{}.txt".format(symbol.replace('/', '')), "w")
        f.write(str(data))
        f.close()


