from rest_framework import serializers


class FuturesStepSerializer(serializers.Serializer):
    entry_price = serializers.FloatField()
    share = serializers.FloatField(required=False, allow_null=True)
    leverage = serializers.IntegerField(required=False, allow_null=True)
    margin = serializers.FloatField(required=False, allow_null=True)
    is_market = serializers.BooleanField(default=False)
    is_triggered = serializers.BooleanField(default=False)
    purchased_size = serializers.FloatField(required=False, allow_null=True)
    cost = serializers.FloatField(required=False, allow_null=True)
