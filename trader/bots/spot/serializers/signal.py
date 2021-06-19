from rest_framework import serializers
from datetime import datetime
from trader.models import SpotSignal


class SpotSignalSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=50)
    steps = serializers.ListField(child=serializers.FloatField())
    targets = serializers.ListField(child=serializers.FloatField())
    stop_loss = serializers.FloatField()

    def create(self, validated_data):
        now = datetime.now()
        signal_id = '{}|{}'.format(self.symbol, now)
        return SpotSignal(signal_id=signal_id, **validated_data)
