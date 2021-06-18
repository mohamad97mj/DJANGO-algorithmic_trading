from rest_framework import serializers
from trader.bots.spot.models import SpotSignal


class SignalSerializer(serializers.Serializer):
    signal_id = serializers.CharField(max_length=100)
    symbol = serializers.CharField(max_length=50)
    steps = serializers.ListField(child=serializers.FloatField())
    targets = serializers.ListField(child=serializers.FloatField())
    stop_loss = serializers.FloatField()
