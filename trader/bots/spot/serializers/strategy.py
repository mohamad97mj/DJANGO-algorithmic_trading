from rest_framework import serializers


class SpotStrategySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    status = serializers.CharField(max_length=50)
