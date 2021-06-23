from datetime import datetime
from rest_framework import serializers
from .position import SpotPositionSerializer
from ..models import SpotPosition


class SpotBotSerializer(serializers.Serializer):
    exchange_id = serializers.CharField(max_length=100)
    credential_id = serializers.CharField(max_length=100)
    strategy = serializers.CharField(max_length=100)
    position = SpotPositionSerializer()
