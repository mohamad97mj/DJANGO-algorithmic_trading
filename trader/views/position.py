from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from djangorestframework_camel_case import render
from django.conf import settings


class MovieDetailView(APIView):
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

        movie = Movie.objects.find(movie_id=movie_id)
        serializer = MovieFullSerializer(MovieFullDtoCreator.get_movie_full_dto(movie, lang=lang))
        data = serializer.data
        return Response(data)
