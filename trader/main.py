from trader.bots.spot_trader_bot import SpotTraderBot
from trader.bots.general_bot import GeneralBot


def main():
    # general_bot = GeneralBot()
    # general_bot.ping_server()
    # general_bot.get_server_time()
    # general_bot.get_symbol_info()
    # general_bot.get_all_coins_info()

    spot_bot = SpotTraderBot()
    spot_bot.get_symbol_all_ordres()
    spot_bot.get_dayli_account_snapshot()


if __name__ == "__main__":
    main()
