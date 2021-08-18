from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from ..services import SpotBotService
from ..serializers import SpotBotSerializer
from global_utils import catch_all_exceptions


class SpotBotsView(APIView):
    renderer_classes = (renderers.JSONRenderer,)

    # permission_classes = [mypermissions.MyCustomIsAuthenticated]
    # @REQUEST_TIME.time()


    @catch_all_exceptions(reraise=True)
    def post(self, request, format=None):
        """
        Opens a new position.
        """

        data = request.data
        bot_serializer = SpotBotSerializer(data=data)

        test_data = None
        if bot_serializer.is_valid():
            bot_instance = SpotBotService.create_bot(bot_serializer.validated_data)
            test_data = SpotBotSerializer(instance=bot_instance).data

        return Response(test_data)


