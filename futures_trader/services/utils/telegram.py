from global_utils.retry_on_timeout import retry_on_timeout


class TelegramApi:

    def __init__(self):
        self._client = self._create_client()

    @retry_on_timeout(timeout_errors=(ConnectionError,))
    def _create_client(self):
        api_id = 764667
        api_hash = 'ffb6562fd4311e1487c60f068f5b74ce'
        phone = '+989059242876'

        client = TelegramClient('{}.session'.format(phone), api_id, api_hash)

        client.connect()
        if not client.is_user_authorized():
            client.sign_in(phone)
            try:
                try:
                    client.sign_in(code=input('Enter code: '))
                except SessionPasswordNeededError:
                    client.sign_in(password=getpass.getpass())
            except EOFError:
                pass
        return client


