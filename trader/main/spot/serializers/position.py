from datetime import datetime
from rest_framework import serializers
from .signal import SpotSignalSerializer
from ..models import SpotPosition


class SpotPositionSerializer(serializers.Serializer):
    signal = SpotSignalSerializer()
    volume = serializers.FloatField()
    strategy = serializers.CharField(max_length=100)

    def create(self, validated_data):
        signal_serializer = SpotSignalSerializer(data=validated_data['signal'])
        if signal_serializer.is_valid():
            signal = signal_serializer.save()

        return SpotPosition(signal=signal,
                            volume=validated_data['volume'],
                            strategy=validated_data['strategy'])
