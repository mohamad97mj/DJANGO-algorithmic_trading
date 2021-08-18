from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.http import QueryDict
from ..services import SpotPositionService
from ..serializers import SpotPositionSerializer, SpotBotSerializer
from django.utils import timezone
from datetime import datetime
import json


class PositionView(APIView):
    renderer_classes = (renderers.JSONRenderer,)

    # permission_classes = [mypermissions.MyCustomIsAuthenticated]
    # @REQUEST_TIME.time()

    def post(self, request, format=None):
        """
        Opens a new position.
        """

        data = request.data
        exchange_id = data['exchange_id']
        credential_id = data['credential_id']
        strategy = data['strategy']
        position_data = data['position']

        position_serializer = SpotPositionSerializer(data=position_data)

        test_data = None
        if position_serializer.is_valid():
            spot_position = position_serializer.save()
            bot_instance = SpotPositionService.open_position(exchange_id=exchange_id,
                                                             credential_id=credential_id,
                                                             strategy=strategy,
                                                             position=spot_position)

            bot_serializer = SpotBotSerializer(instance=bot_instance)
            test_data = bot_serializer.data

        return Response(test_data)

    def put(self, request, format=None):
        bot_id = request.POST.get('bot_id')
        command = request.POST.get('command')

        SpotPositionService.edit_position(bot_id, command)
        return Response({'status': 'ok'})


class PositionStepView(APIView):
    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request, format=None):
        data = request.data
        position_id = data.get('position_id')
        buy_price = data.get('buy_price')
        share = data.get('share')
        SpotPositionService.add_position_step(position_id,
                                              buy_price,
                                              share)
        return Response({'status': 'ok'})

    def put(self, request, format=None):
        data = request.data
        pass
