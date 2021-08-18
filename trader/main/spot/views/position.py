import json
from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from global_utils import catch_all_exceptions
from ..services import SpotBotService
from ..serializers import SpotPositionSerializer


class PositionStepView(APIView):
    renderer_classes = (renderers.JSONRenderer,)

    @catch_all_exceptions(reraise=True)
    def put(self, request, bot_id, format=None):
        body = request.body
        data = json.loads(body)
        steps_data = data['steps']
        step_share_set_mode = data['step_share_set_mode']
        new_position = SpotBotService.edit_position_steps(bot_id,
                                                          steps_data,
                                                          step_share_set_mode)

        position_serializer = SpotPositionSerializer(instance=new_position)
        return Response(position_serializer.data)
