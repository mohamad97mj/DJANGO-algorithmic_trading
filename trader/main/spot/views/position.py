from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from ..services import SpotPositionService
from ..serializers import SpotPositionSerializer, SpotBotSerializer
from django.utils import timezone
from datetime import datetime


class PositionView(APIView):
    renderer_classes = (
        renderers.BrowsableAPIRenderer,
    ) if settings.DEBUG else (
        renderers.JSONRenderer,
    )

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
