import django_tables2 as tables

from ..models import FuturesBot


class FuturesBotTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name="futures_trader/bot_actions.html",
        orderable=False,
    )

    class Meta:
        model = FuturesBot
        template_name = "django_tables2/bootstrap.html"
        fields = (
            'id', 'position__signal__symbol', 'created_at', 'is_active', 'status', 'stopped_at')
