from rest_framework import serializers


class FuturesStoplossSerializer(serializers.Serializer):
    trigger_price = serializers.FloatField()
    is_triggered = serializers.BooleanField(default=False)
