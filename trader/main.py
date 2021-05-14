from trader.bots import GeneralBot, MarketDataBot, SpotTraderBot


def main():
    general_bot = GeneralBot()
    # general_bot.ping_server()
    # general_bot.get_server_time()
    # general_bot.get_symbol_info()
    # general_bot.get_exchange_info()

    # market_bot = MarketDataBot()
    # market_bot.get_recent_trades()
    # market_bot.get24hr_ticker()
    # market_bot.get_symbol_avg_price(symbol='ETHUSDT')
    # market_bot.get_all_prices()

    spot_bot = SpotTraderBot()
    # spot_bot.get_dayli_account_snapshot()
    # spot_bot.get_account_info()
    # spot_bot.place_buy_market_order(symbol='ETHUSDT', quantity=1)
    # spot_bot.get_symbol_all_trades(symbol='ETHUSDT')
    # spot_bot.place_buy_market_order(0.75, symbol='ETHUSDT')
    # spot_bot.place_sell_market_order(0.75, symbol='ETHUSDT')
    # spot_bot.place_buy_limit_order(1.5, 150, symbol='ETHUSDT')
    # spot_bot.place_sell_limit_order(1.25, 210, symbol='ETHUSDT')
    # spot_bot.get_symbol_all_orders('ETHUSDT')
    # spot_bot.get_symbol_all_open_orders('ETHUSDT')
    # spot_bot.get_symbol_all_orders('ETHUSDT')
    spot_bot.get_trade_fees()
    spot_bot.get_symbol_trade_fees()


if __name__ == "__main__":
    main()
