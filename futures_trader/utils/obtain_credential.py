from futures_trader.auth import futures_credentials
from global_utils import CredentialIdDoesNotExistsException


def obtain_credential(credential_id):
    credential = futures_credentials.get(credential_id)
    if not credential:
        raise CredentialIdDoesNotExistsException('credential_id {} does not exists'.format(credential))
    return credential['api_key'], credential['secret'], credential.get('password')
