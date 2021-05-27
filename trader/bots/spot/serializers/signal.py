from rest_framework import serializers
from trader.bots.spot.models import SpotSignal


class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotSignal
        fiedls = '__all__'
