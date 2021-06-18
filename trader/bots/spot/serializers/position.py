from rest_framework import serializers
from .signal import SpotSignalSerializer
from .strategy import SpotStrategySerializer


class SpotPositionSerializer(serializers.Serializer):
    position_id = serializers.CharField(max_length=100)
    signal = SpotSignalSerializer()
    volume = serializers.FloatField()
    strategy = SpotStrategySerializer()
