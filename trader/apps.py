from django.apps import AppConfig


class TraderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trader'

    def ready(self):
        from global_utils import my_get_logger
        logger = my_get_logger()
        logger.info("trader app started!")
        from .trade import trade
        trade()
