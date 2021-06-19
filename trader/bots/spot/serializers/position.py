from rest_framework import serializers
from .signal import SpotSignalSerializer
from .strategy import SpotStrategySerializer
from trader.models import SpotPosition


class SpotPositionSerializer(serializers.Serializer):
    signal = SpotSignalSerializer()
    volume = serializers.FloatField()
    strategy = SpotStrategySerializer()

    def create(self, validated_data):
        signal = SpotSignalSerializer(**validated_data['signal']).save()
        strategy = SpotStrategySerializer(**validated_data['strategy']).save()
        return SpotPosition(position_id=validated_data['position_id'],
                            signal=signal,
                            volume=validated_data['volume'],
                            strategy=strategy)
