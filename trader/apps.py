from django.apps import AppConfig


class TraderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trader'

    def ready(self):
        import asyncio
        from .trade import trade
        asyncio.run(trade())
        print("after")
