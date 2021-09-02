from trader.auth import credentials


def obtain_credential(credential_id):
    credential = credentials[credential_id]
    return credential['api_key'], credential['secret'], credential.get('password')
