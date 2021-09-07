from rest_framework import serializers
from .signal import FuturesSignalSerializer


class FuturesPositionSerializer(serializers.Serializer):
    signal = FuturesSignalSerializer(required=False, allow_null=True)
    size = serializers.FloatField(required=False, allow_null=True)
    margin = serializers.FloatField()
    leverage = serializers.FloatField()
    cost = serializers.FloatField(required=False, allow_null=True)
    keep_open = serializers.BooleanField(required=False, allow_null=True)
