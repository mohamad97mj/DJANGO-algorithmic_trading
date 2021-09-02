from rest_framework import serializers
from .step import FuturesStepSerializer
from .target import FuturesTargetSerializer
from .stoploss import FuturesStoplossSerializer


class FuturesSignalSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=50)
    step_share_set_mode = serializers.CharField(max_length=50, required=False, allow_null=True)
    steps = FuturesStepSerializer(many=True)
    targets = FuturesTargetSerializer(many=True, required=False, allow_null=True)
    stoploss = FuturesStoplossSerializer(required=False, allow_null=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        sorted_steps = sorted(ret['steps'], key=lambda s: s['buy_price'])
        if sorted_steps[0]['buy_price'] == -1:
            sorted_steps.append(sorted_steps.pop(0))
        ret['steps'] = sorted_steps
        ret['targets'] = sorted(ret['targets'], key=lambda s: s['tp_price'])
        return ret
