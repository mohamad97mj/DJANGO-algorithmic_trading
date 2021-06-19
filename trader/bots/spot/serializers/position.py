from rest_framework import serializers
from .signal import SpotSignalSerializer
from .strategy import SpotStrategySerializer
from trader.bots.spot.models import SpotPosition, SpotSignal, SpotStrategy


class SpotPositionSerializer(serializers.Serializer):
    signal = SpotSignalSerializer()
    volume = serializers.FloatField()
    strategy = SpotStrategySerializer()

    def create(self, validated_data):
        signal = SpotSignal(**validated_data['signal'])
        strategy = SpotStrategy(**validated_data['strategy'])
        return SpotPosition(position_id=validated_data['position_id'],
                            signal=signal,
                            volume=validated_data['volume'],
                            strategy=strategy)
