from futures_trader.auth import futures_credentials


def obtain_credential(credential_id):
    credential = futures_credentials[credential_id]
    return credential['api_key'], credential['secret'], credential.get('password')
