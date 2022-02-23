from rest_framework import serializers
from .signal import FuturesSignalSerializer


class FuturesPositionSerializer(serializers.Serializer):
    signal = FuturesSignalSerializer()
    holding_size = serializers.FloatField(required=False, allow_null=True)
    margin = serializers.FloatField()
    order_type = serializers.CharField(max_length=100, default='market')
    keep_open = serializers.BooleanField(required=False, allow_null=True)
