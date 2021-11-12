from rest_framework import serializers


class FuturesTargetSerializer(serializers.Serializer):
    tp_price = serializers.FloatField()
    share = serializers.FloatField(required=False, allow_null=True)
    is_triggered = serializers.BooleanField(default=False)
