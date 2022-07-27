import json
from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from ..services import SpotBotTrader
from ..serializers import SpotBotSerializer
from global_utils import catch_all_exceptions


class SpotBotsView(APIView):
    renderer_classes = (renderers.JSONRenderer,)

    # permission_classes = [mypermissions.MyCustomIsAuthenticated]
    # @REQUEST_TIME.time()

    @catch_all_exceptions()
    def get(self, request, format=None):
        credential_id = request.query_params.get('credential_id', 'kucoin_test')
        is_active = request.query_params.get('is_active', 'false') == 'true'
        bot_instances = SpotBotTrader.get_bots(credential_id=credential_id, is_active=is_active)
        return Response(data=SpotBotSerializer(bot_instances, many=True).data)

    @catch_all_exceptions()
    def post(self, request, format=None):
        """
        Opens a new position.
        """

        data = request.data
        bot_serializer = SpotBotSerializer(data=data)

        bot_data = None
        if bot_serializer.is_valid():
            bot_instance = SpotBotTrader.create_bot(bot_serializer.validated_data)
            bot_data = SpotBotSerializer(instance=bot_instance).data

        return Response(bot_data)


class SpotBotDetailView(APIView):
    @catch_all_exceptions()
    def get(self, request, bot_id, format=None):
        credential_id = request.query_params.get('credential_id', 'kucoin_test')
        bot_instance = SpotBotTrader.get_bot(credential_id=credential_id, bot_id=bot_id)
        return Response(data=SpotBotSerializer(instance=bot_instance).data)

    @catch_all_exceptions()
    def put(self, request, bot_id, format=None):
        data = json.loads(request.body)
        command = data['command']
        credential_id = data.get('credential_id', 'kucoin_test')
        bot_instance = command_mapper[command](credential_id, bot_id)
        return Response(data=SpotBotSerializer(instance=bot_instance).data)


command_mapper = {
    'pause': SpotBotTrader.pause_bot,
    'start': SpotBotTrader.start_bot,
    'stop': SpotBotTrader.stop_bot,
}
