from . import CustomException


class DoesNotExistsException(CustomException):
    code = 404
    message_code = 'ObjectDoesNotExists'
    translated_message = 'آبجکت مورد نظر یافت نشد'


class BotDoesNotExistsException(DoesNotExistsException):
    # code = 404
    message_code = 'BotDoesNotExists'
    translated_message = 'ربات مورد نظر یافت نشد'


class CredentialIdDoesNotExistsException(DoesNotExistsException):
    code = 404
    message_code = 'BotDoesNotExists'
    translated_message = 'کلید مورد نظر یافت نشد'
