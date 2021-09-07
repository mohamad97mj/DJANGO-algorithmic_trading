from rest_framework import serializers


class FuturesStepSerializer(serializers.Serializer):
    buy_price = serializers.FloatField()
    share = serializers.FloatField(required=False, allow_null=True)
    margin = serializers.FloatField(required=False, allow_null=True)
    size = serializers.FloatField(required=False, allow_null=True)
    cost = serializers.FloatField(required=False, allow_null=True)
    is_triggered = serializers.BooleanField(default=False)
