import codecs
import nacl.secret
import nacl.utils
from hkdf import Hkdf
from six import text_type


def _get_nacl_secret_box(secret, hmac_secret):
    if isinstance(secret, text_type):
        secret = secret.encode("utf-8")

    if isinstance(hmac_secret, text_type):
        hmac_secret = hmac_secret.encode("utf-8")

    secret_key = Hkdf(b"", hmac_secret).expand(secret)
    box = nacl.secret.SecretBox(secret_key)
    return box


def encrypt(message, secret, hmac_secret):
    box = _get_nacl_secret_box(secret, hmac_secret)
    message_bytes = message.encode('utf-8')
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    return codecs.encode(box.encrypt(message_bytes, nonce),
                         'hex_codec').decode('utf-8')


def decrypt(encrypted, secret, hmac_secret):
    box = _get_nacl_secret_box(secret, hmac_secret)
    message_bytes = box.decrypt(codecs.decode(encrypted, 'hex_codec'))
    return message_bytes.decode('utf-8')
