import json
from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from global_utils import catch_all_exceptions
from ..services import FuturesBotTrader
from ..serializers import FuturesPositionSerializer


class FuturesPositionView(APIView):
    renderer_classes = (renderers.JSONRenderer,)

    @catch_all_exceptions()
    def put(self, request, bot_id, format=None):
        data = json.loads(request.body)
        credential_id = data.get('credential_id', 'kucoin_test')
        new_position_data = data['position']
        new_position, edited_data = FuturesBotTrader.edit_position(credential_id,
                                                                   new_position_data,
                                                                   bot_id,
                                                                   raise_error=True)

        position_serializer = FuturesPositionSerializer(instance=new_position)
        return Response(
            {
                'edited_data': edited_data,
                'new_position': position_serializer.data
            }
        )
