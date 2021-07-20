class CustomException(Exception):
    code = 1
    message_code = 'custom_exception'
    translated_message = 'خطای سفارشی'

    def __init__(self, message=message_code):
        self.message = message

    def __str__(self):
        return self.message
