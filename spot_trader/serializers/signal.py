from rest_framework import serializers
from .step import SpotStepSerializer
from .target import SpotTargetSerializer
from .stoploss import SpotStoplossSerializer


class SpotSignalSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=50)
    setup_mode = serializers.CharField(max_length=50, required=False, allow_null=True)
    steps = SpotStepSerializer(many=True)
    targets = SpotTargetSerializer(many=True, required=False, allow_null=True)
    stoploss = SpotStoplossSerializer(required=False, allow_null=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        sorted_steps = sorted(ret['steps'], key=lambda s: s['buy_price'])
        if sorted_steps[0]['buy_price'] == -1:
            sorted_steps.append(sorted_steps.pop(0))
        ret['steps'] = sorted_steps
        ret['targets'] = sorted(ret['targets'], key=lambda s: s['tp_price'])
        return ret
