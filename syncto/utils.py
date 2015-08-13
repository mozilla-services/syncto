import base64
import re

from binascii import hexlify
from six import binary_type, text_type
from uuid import UUID

UUID4_VALIDATOR = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-'
                             r'[89ab][0-9a-f]{3}-[0-9a-f]{12}$')


def base64url_decode(input, encoding='utf-8'):
    """Add missing padding and decode from urlsafe base64.

    URL safe base64 is using - and _ instead of + and /.

    """
    if not isinstance(input, binary_type):
        input = text_type(input).encode(encoding)
    rem = len(input) % 4

    if rem > 0:
        input += b'=' * (4 - rem)

    return base64.urlsafe_b64decode(input)


def base64url_encode(input, encoding='utf-8'):
    """Remove padding and encode in urlsafe base64.

    URL safe base64 is using - and _ instead of + and /.

    """
    if not isinstance(input, binary_type):
        input = text_type(input).encode(encoding)
    return base64.urlsafe_b64encode(input).replace(b'=', b'')


def bytes_to_uuid4(bytes_array):
    """Take a byte array and build a valid uuid4."""
    # If we have more that 14 bytes it means that we should provide a
    # valid uuid4
    if len(bytes_array) > 14:
        uuid = text_type(UUID(hexlify(bytes_array).decode('utf-8')))
        if UUID4_VALIDATOR.match(uuid) is None:
            error_msg = 'Your bytes array cannot be converted into an UUID4.'
            raise ValueError(error_msg)
        else:
            bytes_array = bytes_array.ljust(16, b'\x00')
    # If we have less than 14 bytes, we can add two bytes that will
    # fake a valid UUID4
    else:
        bytes_array = bytes_array.ljust(14, b'\x00')
        bytes_array = (bytes_array[:6] +
                       b'\x40' + bytes_array[6:7] +
                       b'\x80' + bytes_array[7:14])

    hexified_bytes = hexlify(bytes_array).decode('utf-8')
    return text_type(UUID(hexified_bytes))


def uuid4_to_bytes(uuid4):
    """Convert a given uuid4 to the right number of bytes.

     - If it is a fully random uuid4, return the 16 bytes
     - If it looks like a manually build uuid4, remove the fake bytes

    """
    bytes_array = UUID(uuid4).bytes

    is_built_uuid4 = (bytes_array[6] in (b'\x40', ord(b'\x40')) and
                      bytes_array[8] in (b'\x80', ord(b'\x80')))
    if is_built_uuid4:
        bytes_array = b''.join((bytes_array[:6],
                                bytes_array[7:8],
                                bytes_array[9:16]))

    return bytes_array.rstrip(b'\x00').ljust(9, b'\x00')


def base64_to_uuid4(base64_id):
    """From base64 to uuid4 ids.

    Extract the bytes from the base64 and encode them in a valid uuid4
    string.

    """
    return bytes_to_uuid4(base64url_decode(base64_id))


def uuid4_to_base64(uuid4_id):
    """From uuid4 to base64 ids.

    Extract the bytes from the uuid4 and encode them in a base64
    string.

    """
    return base64url_encode(uuid4_to_bytes(uuid4_id))
