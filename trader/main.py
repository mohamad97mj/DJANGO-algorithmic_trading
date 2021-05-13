from trader.bots.spot_trader_bot import SpotTraderBot
from trader.bots.general_bot import GeneralBot


def main():
    spot_bot = SpotTraderBot()
    general_bot = GeneralBot()
    # general_bot.ping_server()
    # general_bot.get_server_time()
    general_bot.get_symbol_info()
    # spot_bot.get_symbol_all_ordres()


if __name__ == "__main__":
    main()
