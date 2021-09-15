from rest_framework import serializers


class SpotStoplossSerializer(serializers.Serializer):
    trigger_price = serializers.FloatField()
    is_triggered = serializers.BooleanField(default=False)
