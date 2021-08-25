import json
from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from global_utils import catch_all_exceptions
from ..services import SpotBotTrader
from ..serializers import SpotPositionSerializer


class SpotPositionView(APIView):
    renderer_classes = (renderers.JSONRenderer,)

    @catch_all_exceptions(reraise=True)
    def put(self, request, bot_id, format=None):
        credential_id = request.query_params.get('credential_id', 'test')
        data = json.loads(request.body)
        new_position_data = data['position']
        new_position, edited_data = SpotBotTrader.edit_position(bot_id, credential_id, new_position_data, )

        position_serializer = SpotPositionSerializer(instance=new_position)
        return Response(
            {
                'edited_data': edited_data,
                'new_position': position_serializer.data
            }
        )
