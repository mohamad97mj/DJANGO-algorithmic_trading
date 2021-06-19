from rest_framework import serializers
from .signal import SpotSignalSerializer
from .strategy import SpotStrategySerializer
from trader.models import SpotPosition
from datetime import datetime


class SpotPositionSerializer(serializers.Serializer):
    signal = SpotSignalSerializer()
    volume = serializers.FloatField()
    strategy = SpotStrategySerializer()

    def create(self, validated_data):
        signal_serializer = SpotSignalSerializer(data=validated_data['signal'])
        if signal_serializer.is_valid():
            signal = signal_serializer.save()

        strategy_serializer = SpotStrategySerializer(data=validated_data['strategy'])
        if strategy_serializer.is_valid():
            strategy = strategy_serializer.save()

        return SpotPosition(signal=signal,
                            volume=validated_data['volume'],
                            strategy=strategy)
