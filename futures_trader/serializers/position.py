from rest_framework import serializers
from .signal import FuturesSignalSerializer


class   FuturesPositionSerializer(serializers.Serializer):
    signal = FuturesSignalSerializer()
    holding_size = serializers.FloatField(required=False, allow_null=True)
    margin = serializers.FloatField()
    keep_open = serializers.BooleanField(required=False, allow_null=True)
