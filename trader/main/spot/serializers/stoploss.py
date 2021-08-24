from rest_framework import serializers


class SpotStoplossSerializer(serializers.Serializer):
    trigger_price = serializers.FloatField()
    amount = serializers.FloatField(required=False)
    is_triggered = serializers.BooleanField(default=False)
