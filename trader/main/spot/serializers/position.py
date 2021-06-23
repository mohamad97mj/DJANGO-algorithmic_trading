from datetime import datetime
from rest_framework import serializers
from .signal import SpotSignalSerializer
from ..models import SpotPosition


class SpotPositionSerializer(serializers.Serializer):
    signal = SpotSignalSerializer(required=False, allow_null=True)
    volume = serializers.FloatField()
    strategy = serializers.CharField(max_length=100)

    def create(self, validated_data):
        signal = None
        if validated_data['signal']:
            signal_serializer = SpotSignalSerializer(data=validated_data['signal'])
            if signal_serializer.is_valid():
                signal = signal_serializer.save()

        return SpotPosition(signal=signal,
                            **{k: validated_data[k] for k in ['volume', 'strategy']}
                            )
