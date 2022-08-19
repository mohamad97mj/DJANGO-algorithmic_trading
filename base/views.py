from django.shortcuts import render
from datetime import datetime, timedelta
# Create your views here.

from rest_framework.views import APIView


class HomeView(APIView):

    def get(self, request):
        last_hour_datetime = datetime.now() - timedelta(minutes=25)
        from_date = '{}-{}-{}'.format(last_hour_datetime.year,
                                      str(last_hour_datetime.month).zfill(2),
                                      str(last_hour_datetime.day).zfill(2))
        from_time = '{}%3A25'.format(str(last_hour_datetime.hour).zfill(2))
        contex = {
            'from_date': from_date,
            'from_time': from_time,
        }

        return render(request, 'base/home.html', context=contex)
