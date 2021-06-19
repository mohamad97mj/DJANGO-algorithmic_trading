from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from djangorestframework_camel_case import render
from django.conf import settings
from trader.serializers import SpotPositionSerializer
from trader.models import SpotPosition


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
        serializer = SpotPositionSerializer(data=data)
        test_data = None
        if serializer.is_valid():
            spot_position = serializer.save()
            test_data = SpotPositionSerializer(instance=spot_position).data
        return Response(test_data)
