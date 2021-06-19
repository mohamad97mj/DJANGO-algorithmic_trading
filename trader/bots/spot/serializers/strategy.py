from rest_framework import serializers
from trader.models import SpotStrategy


class SpotStrategySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    status = serializers.CharField(max_length=50)

    def create(self, validated_data):
        now = datetime.now()
        strategy_id = '{}|{}'.format(self.symbol, now)
        return SpotStrategy(strategy_id=strategy_id, **validated_data)
