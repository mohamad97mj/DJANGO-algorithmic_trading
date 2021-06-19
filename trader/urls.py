from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = 'trader'

urlpatterns = [
    path('spot-positions', views.PositionView.as_view(), name='spot_position'),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
