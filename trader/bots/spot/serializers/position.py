from rest_framework import serializers
from .signal import SpotSignalSerializer


class SpotPositionSerializer(serializers.Serializer):
    position_id = serializers.CharField(max_length=100)
    signal = SpotSignalSerializer()
    volume = serializers.FloatField()
    strategy = models.OneToOneField('SpotStrategy', related_name='position', on_delete=models.RESTRICT)
