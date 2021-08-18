from rest_framework import serializers
from .signal import SpotSignalSerializer


class SpotStepSerializer(serializers.Serializer):
    signal = SpotSignalSerializer()
    share = serializers.FloatField()
