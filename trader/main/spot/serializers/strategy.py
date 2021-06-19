from datetime import datetime
from rest_framework import serializers
from ..models import SpotStrategy


class SpotStrategySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    status = serializers.CharField(max_length=50)

    def create(self, validated_data):
        return SpotStrategy(**validated_data)
