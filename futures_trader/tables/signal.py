import django_tables2 as tables

from ..models import FuturesSignal


class FuturesSignalTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name="futures_trader/signal_actions.html",
        orderable=False,
    )

    class Meta:
        model = FuturesSignal
        template_name = "django_tables2/bootstrap.html"
        fields = ('id', 'symbol', 'side', 'created_at', 'confirmations', 'status')
