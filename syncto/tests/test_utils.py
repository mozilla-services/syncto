import os
import unittest

from binascii import hexlify
from six import text_type, binary_type
from uuid import uuid4, UUID

from syncto.utils import (
    bytes_to_uuid4, UUID4_VALIDATOR, uuid4_to_bytes, base64url_encode,
    base64_to_uuid4, uuid4_to_base64, base64url_decode
)


def generate_random_uuid4():
    return text_type(uuid4())


def generate_made_up_uuid4():
    uuid_bytes = list(uuid4().bytes)
    uuid_bytes[6] = binary_type('\x40')
    uuid_bytes[8] = binary_type('\x80')
    uuid = UUID(hexlify(binary_type(''.join(uuid_bytes))))
    return text_type(uuid)


class Bytes2UUID4Test(unittest.TestCase):
    def test_a_wrong_uuid4_array_fails(self):
        try:
            bytes_to_uuid4(os.urandom(16))
        except ValueError:
            pass
        else:
            self.fail("16 random bytes shouldn't make a valid UUID4")

    def test_bytes_are_valids_uuid4(self):
        valid = UUID4_VALIDATOR.match(bytes_to_uuid4(os.urandom(14)))
        if valid is None:
            self.fail("14 random bytes should make a valid UUID4")


class UUID4ToBytesTest(unittest.TestCase):
    def test_a_basic_uuid4_returns_14_bytes(self):
        uuid = generate_made_up_uuid4()
        uuid_bytes = uuid4_to_bytes(uuid)
        if len(uuid_bytes) > 14:
            self.fail("A made uuid4 should return 14 bytes of data. "
                      "Returned %s" % len(uuid_bytes))

    def test_a_random_uuid4_returns_16_bytes(self):
        uuid = generate_random_uuid4()
        uuid_bytes = uuid4_to_bytes(uuid)
        if len(uuid_bytes) != 16:
            self.fail("A full random uuid4 should return 16 bytes of data. "
                      "Returned %s" % len(uuid_bytes))


class UUID4ConverterIdempotenceTest(unittest.TestCase):

    def test_a_random_uuid4_should_return_the_same_uuid4(self):
        uuid = generate_random_uuid4()
        uuid_bytes = uuid4_to_bytes(uuid)
        bytes_uuid = bytes_to_uuid4(uuid_bytes)
        self.assertEqual(uuid, bytes_uuid)

    def test_a_made_up_uuid4_should_return_the_same_uuid4(self):
        uuid = generate_made_up_uuid4()
        uuid_bytes = uuid4_to_bytes(uuid)
        bytes_uuid = bytes_to_uuid4(uuid_bytes)
        self.assertEqual(uuid, bytes_uuid)


class Base64ToUUIDConverterIdempotenceTest(unittest.TestCase):

    def test_a_base64_id_converted_to_an_uuid4_id_returns_the_same_id(self):
        base64_id = base64url_encode(os.urandom(9))
        uuid4_id = base64_to_uuid4(base64_id)
        computed_base64_id = uuid4_to_base64(uuid4_id)
        self.assertEqual(base64_id, computed_base64_id)

    def test_a_uuid4_id_converted_to_a_base64_id_returns_the_same_id(self):
        uuid4_id = generate_random_uuid4()
        base64_id = uuid4_to_base64(uuid4_id)
        computed_uuid4_id = base64_to_uuid4(base64_id)
        self.assertEqual(uuid4_id, computed_uuid4_id)


class Base64urlEncoderDecoderTest(unittest.TestCase):

    def test_base64url_decode_handle_unicode(self):
        string = base64url_encode(os.urandom(16)).decode('utf-8')
        self.assertTrue(isinstance(string, text_type), type(string))
        decoded = base64url_decode(string)
        self.assertTrue(isinstance(decoded, binary_type), type(string))

    def test_base64url_encode_handle_unicode(self):
        string = text_type("foobar")
        self.assertTrue(isinstance(string, text_type), type(string))
        decoded = base64url_encode(string)
        self.assertTrue(isinstance(decoded, binary_type), type(string))
