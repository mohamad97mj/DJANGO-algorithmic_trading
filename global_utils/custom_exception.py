class CustomException(Exception):
    code = 500
    message_code = 'custom_exception'
    translated_message = 'خطای سفارشی'
    detail = ''

    def __init__(self, detail=detail):
        self.detail = detail

    def __str__(self):
        return self.detail
