from spot_trader.auth import spot_credentials


def obtain_credential(credential_id):
    credential = spot_credentials[credential_id]
    return credential['api_key'], credential['secret'], credential.get('password')
