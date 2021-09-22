import sys
from django.apps import AppConfig
from .utils.app_vars import enable_futures


class FuturesTraderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'futures_trader'

    def ready(self):
        if enable_futures and not any(
                c in sys.argv for c in ['makemigrations', 'migrate', 'startapp', 'collectstatic']):
            from global_utils import my_get_logger
            logger = my_get_logger()
            logger.info("futures_trader app started!")
            from futures_trader.trade import trade
            trade()
