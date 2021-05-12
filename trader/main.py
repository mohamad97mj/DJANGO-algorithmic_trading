from trader.spot_bot import SpotBotClient


def main():
    spot_bot = SpotBotClient()
    # spot_bot.get_exchange_info()
    spot_bot.get_symbol_all_ordres()


if __name__ == "__main__":
    main()
