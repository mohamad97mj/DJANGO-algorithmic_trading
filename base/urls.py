from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name = 'spot_trader'

urlpatterns = [
    path('',
         views.HomeView.as_view(),
         name='home'),
]


