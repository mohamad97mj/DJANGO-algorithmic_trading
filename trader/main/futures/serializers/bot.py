from datetime import datetime
from rest_framework import serializers
from .position import SpotPositionSerializer


class SpotBotSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    exchange_id = serializers.CharField(max_length=100)
    credential_id = serializers.CharField(max_length=100)
    strategy = serializers.CharField(max_length=100)
    is_active = serializers.BooleanField(required=False)
    status = serializers.CharField(max_length=100, required=False)
    position = SpotPositionSerializer()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.strategy_state_data:
            ret['strategy_state_data'] = instance.strategy_state_data.to_json()
        return ret
