from trader.bots import GeneralBot, MarketDataBot, SpotTraderBot


def main():
    # general_bot = GeneralBot()
    # general_bot.ping_server()
    # general_bot.get_server_time()
    # general_bot.get_symbol_info()

    market_bot = MarketDataBot()
    # market_bot.get_recent_trades()
    # market_bot.get24hr_ticker()
    # market_bot.get_symbol_avg_price(symbol='ETHUSDT')
    # market_bot.get_all_prices()

    spot_bot = SpotTraderBot()
    # spot_bot.get_symbol_all_ordres()
    # spot_bot.get_dayli_account_snapshot()


if __name__ == "__main__":
    main()
