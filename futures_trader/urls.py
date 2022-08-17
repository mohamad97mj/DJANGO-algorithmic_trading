from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = 'futures_trader'

urlpatterns = [
    path('bots/',
         views.FuturesBotsView.as_view(),
         name='futures_bots'),

    path('bot-list/',
         views.FuturesBotListView.as_view(),
         name='futures_bot_list'),

    path('signal-list/',
         views.FuturesSignalListView.as_view(),
         name='futures_signal_list'),

    path('signal-action/<slug:signal_id>',
         views.FuturesSignalActionView.as_view(),
         name='futures_signal_action'),

    path('bots/<int:bot_id>/',
         views.FuturesBotDetailView.as_view(),
         name='futures_bot_detail'),

    path('bots/<int:bot_id>/position/',
         views.FuturesPositionView.as_view(),
         name='futures_bots_position'),

    path('price-monitor/<slug:cache_name>/<slug:location>/',
         views.FuturesPriceMonitorView.as_view(),
         name='futures_price_monitor'),

    path('risky-bots-monitor/',
         views.FuturesRiskyBotsView.as_view(),
         name='futures_risky_bots_monitor')
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
