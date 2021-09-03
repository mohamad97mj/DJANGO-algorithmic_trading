from rest_framework import serializers


class SpotStepSerializer(serializers.Serializer):
    buy_price = serializers.FloatField()
    share = serializers.FloatField(required=False, allow_null=True)
    amount_in_quote = serializers.FloatField(required=False)
    is_triggered = serializers.BooleanField(default=False)
