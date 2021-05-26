from rest_framework import serializers
from trader.bots.spot.models import Signal


class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fiedls = '__all__'
