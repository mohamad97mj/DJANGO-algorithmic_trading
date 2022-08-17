import django_tables2 as tables

from ..models import FuturesBot


class FuturesBotTable(tables.Table):
    class Meta:
        model = FuturesBot
        template_name = "django_tables2/bootstrap.html"
        # fields = ("",)
