from rest_framework import serializers


class SpotStrategySerializer(serializers.Serializer):
    strategy_id = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=200)
    status = serializers.CharField(max_length=50)
