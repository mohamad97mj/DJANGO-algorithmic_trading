from rest_framework import serializers
from .step import FuturesStepSerializer
from .target import FuturesTargetSerializer
from .stoploss import FuturesStoplossSerializer


class FuturesSignalSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=50)
    side = serializers.CharField(max_length=10)
    step_share_set_mode = serializers.CharField(max_length=50, required=False, allow_null=True)
    steps = FuturesStepSerializer(many=True)
    targets = FuturesTargetSerializer(many=True, required=False, allow_null=True)
    stoploss = FuturesStoplossSerializer(required=False, allow_null=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        is_reversed = instance.side == 'sell'
        sorted_steps = sorted(ret['steps'], reverse=is_reversed, key=lambda s: s['entry_price'])
        if sorted_steps[0]['entry_price'] == -1:
            sorted_steps.append(sorted_steps.pop(0))
        ret['steps'] = sorted_steps
        ret['targets'] = sorted(ret['targets'], reverse=is_reversed, key=lambda s: s['tp_price'])
        return ret
