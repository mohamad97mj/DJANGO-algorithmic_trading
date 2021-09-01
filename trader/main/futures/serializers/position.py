from rest_framework import serializers
from .signal import SpotSignalSerializer


class SpotPositionSerializer(serializers.Serializer):
    signal = SpotSignalSerializer(required=False, allow_null=True)
    size = serializers.FloatField()
    keep_open = serializers.BooleanField(required=False, allow_null=True)
