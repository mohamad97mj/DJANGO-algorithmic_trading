from rest_framework import serializers


class SpotTargetSerializer(serializers.Serializer):
    tp_price = serializers.FloatField()
    share = serializers.FloatField(required=False, allow_null=True)
    purchased_amount = serializers.FloatField(required=False)
    is_triggered = serializers.BooleanField(default=False)
