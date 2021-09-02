from rest_framework import serializers


class FuturesTargetSerializer(serializers.Serializer):
    tp_price = serializers.FloatField()
    is_triggered = serializers.BooleanField(default=False)
