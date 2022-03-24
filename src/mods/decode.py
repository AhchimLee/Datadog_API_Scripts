from cryptography.fernet import Fernet

with open('/dd_key/a', 'rb') as fkey:
    key = fkey.read()
fernet = Fernet(key)

def api_key():
    with open('/dd_key/api_key.enc', 'rb') as enc_file:
        api_key_enc = enc_file.read()
    api_key_dec = fernet.decrypt(api_key_enc)
    api_key = api_key_dec.rstrip().decode('utf-8')

    return api_key

def app_key():
    with open('/dd_key/app_key.enc', 'rb') as enc_file:
        app_key_enc = enc_file.read()
    app_key_dec = fernet.decrypt(app_key_enc)
    app_key = app_key_dec.rstrip().decode('utf-8')

    return app_key


