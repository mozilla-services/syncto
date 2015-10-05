import codecs
import hashlib
import hmac
import math
import nacl.secret
import nacl.utils
from six import text_type
from six.moves import range


def HKDF_expand(PRK, info, L, hashmod=hashlib.sha256):
    """HKDF-Expand; see RFC-5869 for the details."""
    digest_size = hashmod().digest_size
    N = int(math.ceil(L * 1.0 / digest_size))
    assert N <= 255
    T = b""
    output = []
    for i in range(1, N + 1):
        data = T + info + chr(i).encode("utf-8")
        T = hmac.new(PRK, data, hashmod).digest()
        output.append(T)
    return b"".join(output)[:L]


def HKDF(secret, salt, info, size, hashmod=hashlib.sha256):
    """HKDF-extract-and-expand as a single function."""
    if isinstance(secret, text_type):
        secret = secret.encode("utf-8")

    if isinstance(salt, text_type):
        salt = salt.encode("utf-8")

    if isinstance(info, text_type):
        info = info.encode("utf-8")

    PRK = hmac.new(salt, secret, hashmod).digest()
    return HKDF_expand(PRK, info, size, hashmod)


def get_nacl_secret_box(client_state, hmac_secret):
    if isinstance(client_state, text_type):
        client_state = client_state.encode("utf-8")

    secret_key = HKDF(client_state, "", hmac_secret, 32)
    box = nacl.secret.SecretBox(secret_key)
    return box


def encrypt(message, client_state, hmac_secret):
    box = get_nacl_secret_box(client_state, hmac_secret)
    message_bytes = message.encode('utf-8')
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
    return codecs.encode(box.encrypt(message_bytes, nonce),
                         'hex_codec').decode('utf-8')


def decrypt(encrypted, client_state, hmac_secret):
    box = get_nacl_secret_box(client_state, hmac_secret)
    message_bytes = box.decrypt(codecs.decode(encrypted, 'hex_codec'))
    return message_bytes.decode('utf-8')
