from django.apps import AppConfig


class TraderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trader'

    def ready(self):
        from datetime import datetime
        print(datetime.now())
        from .trade import trade
        trade()
