from spot_trader.clients.public_client import PublicClient

symbols = [
    '1INCH/USDT',
    'AAVE/USDT',
    'ADA/USDT',
    'ALGO/USDT',
    'APE/USDT',
    'ATOM/USDT',
    'AVAX/USDT',
    'AXS/USDT',
    'BAT/USDT',
    'BCH/USDT',
    'BNB/USDT',
    'BTC/USDT',
    'CELO/USDT',
    'CHZ/USDT',
    'COMP/USDT',
    'CRO/USDT',
    'CRV/USDT',
    'DASH/USDT',
    'DOGE/USDT',
    'DOT/USDT',
    'EGLD/USDT',
    'ENJ/USDT',
    'EOS/USDT',
    'ETC/USDT',
    'ETH/USDT',
    'FIL/USDT',
    'FLOW/USDT',
    'FTM/USDT',
    'GRT/USDT',
    'HBAR/USDT',
    'ICP/USDT',
    'KSM/USDT',
    'LINK/USDT',
    'LRC/USDT',
    'LTC/USDT',
    'LUNA/USDT',
    'MANA/USDT',
    'MATIC/USDT',
    'MKR/USDT',
    'NEAR/USDT',
    'NEO/USDT',
    'ONE/USDT',
    'ROSE/USDT',
    'SAND/USDT',
    'SOL/USDT',
    'SUSHI/USDT',
    'THETA/USDT',
    'TRX/USDT',
    'UNI/USDT',
    'VET/USDT',
    'WAVES/USDT',
    'XLM/USDT',
    'ZEC/USDT'
]


def save_ohlc_data():
    pb = PublicClient()
    for symbol in symbols:
        data = pb.fetch_ohlcv(
            symbol=symbol,
            timeframe='1h',
            limit=720,
        )
        f = open("data/ohlcv/{}.txt".format(symbol.replace('/', '')), "w")
        f.write(str(data))
        f.close()
