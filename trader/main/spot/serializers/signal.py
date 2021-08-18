from rest_framework import serializers
from .step import SpotStepSerializer
from .target import SpotTargetSerializer


class SpotSignalSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=50)
    step_share_set_mode = serializers.CharField(max_length=50)
    steps = SpotStepSerializer(many=True)
    target_share_set_mode = serializers.CharField(max_length=50)
    targets = SpotTargetSerializer(many=True)
    stoploss = serializers.FloatField(required=False, allow_null=True)
