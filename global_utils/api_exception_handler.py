import os
import traceback
from .custom_exception import CustomException
from rest_framework.response import Response
from global_utils.my_logging import my_get_logger
from django.conf import settings


def custom_api_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.

    # response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    # if response is not None:
    #     response.data['status_code'] = response.status_code
    logger = my_get_logger()
    logger.exception(exc)

    response = None
    status = 200
    if isinstance(exc, CustomException):
        status = exc.code
        response = {
            'code': exc.code,
            'messageCode': exc.message_code,
            'translatedMessage': exc.translated_message,
            'detail': exc.detail
        }
    elif isinstance(exc, Exception):
        status = 500
        response = {
            'code': 500,
            'messageCode': "InternalServerError",
            'translatedMessage': "خطای داخلی سرور",
            'detail': exc.args[0]
        }

    return Response(response, status=status)
