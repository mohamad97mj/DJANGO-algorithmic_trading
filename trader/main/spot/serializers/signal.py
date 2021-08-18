from rest_framework import serializers
from .step import SpotStepSerializer
from .target import SpotTargetSerializer


class SpotSignalSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=50)
    step_share_set_mode = serializers.CharField(max_length=50, required=False, allow_null=True)
    steps = SpotStepSerializer(many=True)
    target_share_set_mode = serializers.CharField(max_length=50, required=False, allow_null=True)
    targets = SpotTargetSerializer(many=True, required=False, allow_null=True)
    stoploss = serializers.FloatField(required=False, allow_null=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['steps'] = sorted(ret['steps'], key=lambda s: s['buy_price'])
        ret['targets'] = sorted(ret['targets'], key=lambda s: s['tp_price'])
        return ret
