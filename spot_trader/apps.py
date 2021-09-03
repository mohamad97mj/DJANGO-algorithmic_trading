import sys
from django.apps import AppConfig


class SpotTraderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spot_trader'

    def ready(self):
        if 'runserver' in sys.argv:
            from global_utils import my_get_logger
            logger = my_get_logger()
            logger.info("spot_trader app started!")
            from spot_trader.trade import trade
            trade()
