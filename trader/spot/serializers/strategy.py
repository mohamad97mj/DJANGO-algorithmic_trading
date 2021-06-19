from rest_framework import serializers
from trader.models import SpotStrategy
from datetime import datetime


class SpotStrategySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    status = serializers.CharField(max_length=50)

    def create(self, validated_data):
        return SpotStrategy(**validated_data)
