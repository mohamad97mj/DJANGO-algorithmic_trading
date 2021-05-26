from rest_framework import serializers
from trader.models import Signal


class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fiedls = '__all__'
