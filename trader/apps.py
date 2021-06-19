from django.apps import AppConfig


class TraderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trader'

    def ready(self):
        import asyncio
        from .main import main
        # asyncio.get_event_loop().run_until_complete(main())
