from rest_framework import serializers
from trader.models import signal


class SignalSerializer(serializers.ModelSerializer):
    class Meta:
        model = signal
        fiedls = '__all__'
