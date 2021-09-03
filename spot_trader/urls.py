from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = 'spot_trader'

urlpatterns = [
    path('bots/',
         views.SpotBotsView.as_view(),
         name='spot_bots'),

    path('bots/<slug:bot_id>/',
         views.SpotBotDetailView.as_view(),
         name='spot_bot_detail'),

    path('bots/<slug:bot_id>/position/',
         views.SpotPositionView.as_view(),
         name='spot_bots_position'),

    path('price-monitor/<slug:cache_name>/<slug:location>/',
         views.SpotPriceMonitorView.as_view(),
         name='spot_price_monitor')
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])

