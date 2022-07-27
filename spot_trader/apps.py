import sys
from django.apps import AppConfig
from .utils.app_vars import enable_spot


class SpotTraderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spot_trader'

    def ready(self):
        if enable_spot and not any(
                c in arg for c in ['celery', 'makemigrations', 'migrate', 'startapp', 'collectstatic'] for arg in
                sys.argv):
            from global_utils import my_get_logger
            logger = my_get_logger()
            logger.info("spot_trader app started!")
            from spot_trader.trade import trade
            trade()
