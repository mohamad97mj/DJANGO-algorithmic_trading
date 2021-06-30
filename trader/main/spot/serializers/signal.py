from datetime import datetime
from rest_framework import serializers
from ..models import SpotSignal


class SpotSignalSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=50)
    steps = serializers.ListField(child=serializers.FloatField())
    targets = serializers.ListField(child=serializers.FloatField())
    stoploss = serializers.FloatField()

    def create(self, validated_data):
        spot_signal = SpotSignal(**validated_data)
        spot_signal.save()
        return spot_signal
