from rest_framework import serializers


class FuturesStoplossSerializer(serializers.Serializer):
    trigger_price = serializers.FloatField()
    size = serializers.FloatField(required=False)
    is_triggered = serializers.BooleanField(default=False)
