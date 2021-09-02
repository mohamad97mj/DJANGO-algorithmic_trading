from trader.auth import spot_credentials, futures_credentials


def obtain_credential(credential_id, market):
    credential = spot_credentials[credential_id] if market == 'spot' else futures_credentials[credential_id]
    return credential['api_key'], credential['secret'], credential.get('password')
