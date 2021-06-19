from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from djangorestframework_camel_case import render
from django.conf import settings
from ..services import SpotPositionService
from ..serializers import SpotPositionSerializer


class PositionView(APIView):
    renderer_classes = (
        render.CamelCaseJSONRenderer,
        renderers.BrowsableAPIRenderer,
    ) if settings.DEBUG else (
        render.CamelCaseJSONRenderer,
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
        position_data = data['position']

        serializer = SpotPositionSerializer(data=position_data)

        test_data = None
        if serializer.is_valid():
            spot_position = serializer.save()
            SpotPositionService.open_position(exchange_id=exchange_id,
                                              credential_id=credential_id,
                                              position=spot_position)

            test_data = SpotPositionSerializer(instance=spot_position).data

        return Response(test_data)
