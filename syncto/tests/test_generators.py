import os
from binascii import hexlify
from six import text_type
from uuid import uuid4, UUID

from syncto.utils import (
    bytes_to_uuid4, UUID4_VALIDATOR, uuid4_to_bytes,
    base64_to_uuid4, uuid4_to_base64
)


def generate_random_uuid4():
    return text_type(uuid4())


def generate_made_up_uuid4():
    uuid_bytes = bytearray(uuid4().bytes)
    uuid_bytes[6] = ord(b'\x40')
    uuid_bytes[8] = ord(b'\x80')
    uuid = UUID(hexlify(uuid_bytes).decode('utf-8'))
    return text_type(uuid)


def generate_firefox_sync_id():
    return bytes_to_uuid4(os.urandom(9))


FAKE_UUID4 = generate_made_up_uuid4()
RANDOM_UUID4 = generate_random_uuid4()
FIREFOX_SYNC_UUID4 = generate_firefox_sync_id()

MADE_UP_UUID4 = [FAKE_UUID4,  FIREFOX_SYNC_UUID4]
VALID_UUID4 = MADE_UP_UUID4 + [RANDOM_UUID4]
WRONG_UUID4 = '2bda2998-d9b0-ee19-7da1-42a0447f6725'


def assert_equal(uuid1, uuid2):
    assert uuid1 == uuid2, "%s doesn't equals %s" % (uuid1, uuid2)


def test_validator_validates_valid_uuid4():
    """VALID_UUID4 are accepted by the validator."""

    def assert_valid(validator):
        assert validator, "14 random bytes should make a valid UUID4"

    for uuid in VALID_UUID4:
        validator = UUID4_VALIDATOR.match(uuid)
        yield assert_valid, validator


def test_made_up_uuid4_have_less_than_15_bytes():
    """MADE_UP_UUID4 have less than 15 bytes of information."""

    def assert_uuid_length(uuid_bytes):
        assert len(uuid_bytes) <= 14, (
            "A made uuid4 should return 14 bytes of data. "
            "Returned %s" % len(uuid_bytes))

    for uuid in MADE_UP_UUID4:
        uuid_bytes = uuid4_to_bytes(uuid)
        yield assert_uuid_length, uuid_bytes


def test_a_uuid4_converted_to_bytes_should_return_the_same_uuid4():
    """VALID_UUID4 converted to bytes and back to uuid4 are the same."""
    for uuid in VALID_UUID4:
        uuid_bytes = uuid4_to_bytes(uuid)
        bytes_uuid = bytes_to_uuid4(uuid_bytes)
        yield assert_equal, uuid, bytes_uuid


def test_a_uuid4_id_converted_to_a_base64_id_returns_the_same_id():
    """VALID_UUID4 converted to base64 and back to uuid4 are the same."""
    for uuid in VALID_UUID4:
        base64_id = uuid4_to_base64(uuid)
        computed_uuid4_id = base64_to_uuid4(base64_id)
        yield assert_equal, uuid, computed_uuid4_id
