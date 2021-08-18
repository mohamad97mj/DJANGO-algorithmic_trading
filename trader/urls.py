from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = 'trader'

urlpatterns = [
    path('spot-bots/',
         views.SpotBotsView.as_view(),
         name='spot_bots'),

    path('spot-bots/<slug:bot_id>/',
         views.SpotBotDetailView.as_view(),
         name='spot_bot_detail'),

    path('spot-bots/<slug:bot_id>/position/steps/',
         views.PositionStepView.as_view(),
         name='spot_bots_position_step'),

    path('spot-bots/<slug:bot_id>/position/targets/',
         views.PositionStepView.as_view(),
         name='spot_bots_position_target'),

    path('memory-cache-content/<slug:cache_name>/<slug:location>/',
         views.MemoryCacheContentView.as_view(),
         name='memory_cache_content')
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
