import base64
import re

from binascii import hexlify
from six import binary_type, text_type
from uuid import UUID

UUID4_VALIDATOR = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-'
                             r'[89ab][0-9a-f]{3}-[0-9a-f]{12}$')


def base64url_decode(input, encoding='utf-8'):
    if not isinstance(input, binary_type):
        input = text_type(input).encode(encoding)
    rem = len(input) % 4

    if rem > 0:
        input += b'=' * (4 - rem)

    return base64.urlsafe_b64decode(input)


def base64url_encode(input, encoding='utf-8'):
    if not isinstance(input, binary_type):
        input = text_type(input).encode(encoding)
    return base64.urlsafe_b64encode(input).replace(b'=', b'')


def bytes_to_uuid4(bytes_array):
    if len(bytes_array) > 14:
        uuid = text_type(UUID(hexlify(bytes_array)))
        if UUID4_VALIDATOR.match(uuid) is None:
            raise ValueError('Your bytes array cannot be '
                             'converted into an UUID4.')
        else:
            bytes_array = bytes_array.ljust(16, '\x00')
    else:
        bytes_array = bytes_array.ljust(14, '\x00')
        bytes_array = '%s\x40%s\x80%s' % (bytes_array[:6],
                                          bytes_array[6:7],
                                          bytes_array[7:14])

    return text_type(UUID(hexlify(bytes_array)))


def uuid4_to_bytes(uuid4):
    bytes_array = UUID(uuid4).bytes
    if bytes_array[6] == '\x40' and bytes_array[8] == '\x80':
        bytes_array = '%s%s%s' % (bytes_array[:6],
                                  bytes_array[7:8],
                                  bytes_array[9:16])
    return bytes_array.rstrip('\x00').ljust(9, '\x00')


def base64_to_uuid4(base64_id):
    return bytes_to_uuid4(base64url_decode(base64_id))


def uuid4_to_base64(uuid4_id):
    return base64url_encode(uuid4_to_bytes(uuid4_id))
