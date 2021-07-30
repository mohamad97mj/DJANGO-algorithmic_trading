from datetime import datetime
from rest_framework import serializers
from .signal import SpotSignalSerializer
from ..models import SpotPosition


class SpotPositionSerializer(serializers.Serializer):
    signal = SpotSignalSerializer(allow_null=True)
    volume = serializers.FloatField()

    def create(self, validated_data):
        signal = None
        if validated_data['signal']:
            signal_serializer = SpotSignalSerializer(data=validated_data['signal'])
            if signal_serializer.is_valid():
                signal = signal_serializer.save()

        spot_position = SpotPosition(signal=signal,
                                     **{k: validated_data[k] for k in ['volume']})

        spot_position.save()
        return spot_position
