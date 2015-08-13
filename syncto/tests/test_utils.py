import os
import unittest
from uuid import UUID

from six import text_type, binary_type

from syncto.utils import (
    bytes_to_uuid4, uuid4_to_bytes, base64url_encode, base64url_decode
)
from syncto.tests.test_generators import generate_random_uuid4

WRONG_UUID4 = '2bda2998-d9b0-ee19-7da1-42a0447f6725'


class Bytes2UUID4Test(unittest.TestCase):
    def test_a_wrong_uuid4_array_fails(self):
        try:
            bytes_to_uuid4(UUID(WRONG_UUID4).bytes)
        except ValueError:
            pass
        else:
            self.fail("16 random bytes shouldn't make a valid UUID4")


class UUID4ToBytesTest(unittest.TestCase):
    def test_a_random_uuid4_returns_16_bytes(self):
        uuid_bytes = uuid4_to_bytes(generate_random_uuid4())
        if len(uuid_bytes) != 16:
            self.fail("A full random uuid4 should return 16 bytes of data. "
                      "Returned %s" % len(uuid_bytes))


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
