from __future__ import unicode_literals
import nacl.secret
import re
from six import binary_type, text_type

from syncto import crypto
from syncto.tests.support import unittest


class CryptoTest(unittest.TestCase):
    def test_HKDF_encode_secret_salt_info_if_text_type(self):
        hkdf = crypto.HKDF("Secret", "Salt", "Info", 32)
        self.assertIsInstance(hkdf, binary_type)

    def test_HKDF_also_accept_secret_salt_info_in_bytes(self):
        PRK = crypto.HKDF("Secret".encode('utf-8'),
                          "Salt".encode('utf-8'),
                          "Info".encode('utf-8'), 32)
        self.assertIsInstance(PRK, binary_type)

    def test_HKDF_return_right_number_of_bytes(self):
        hkdf = crypto.HKDF("IKM".encode('utf-8'), "", "Foobar", 32)
        self.assertIsInstance(hkdf, binary_type)
        self.assertEquals(len(hkdf), 32)

    def test_get_nacl_secret_box_encode_client_state_if_text_type(self):
        box = crypto.get_nacl_secret_box("Client State", "HMAC secret")
        self.assertIsInstance(box, nacl.secret.SecretBox)

    def test_get_nacl_secret_box_accept_client_state_as_bytes(self):
        box = crypto.get_nacl_secret_box("Client State".encode('utf-8'),
                                         "HMAC secret")
        self.assertIsInstance(box, nacl.secret.SecretBox)

    def test_encrypt_can_be_decrypted(self):
        message = "Salut la companie"
        encrypted = crypto.encrypt(message, "Client State", "Secret")
        decrypted = crypto.decrypt(encrypted, "Client State", "Secret")
        self.assertEquals(message, decrypted)

    def test_encrypt_returns_hex_encoded_string(self):
        message = "Salut la companie"
        encrypted = crypto.encrypt(message, "Client State", "Secret")
        hex_regexp = re.compile(r'[0-9a-f]+')
        self.assertTrue(hex_regexp.match(encrypted))

    def test_decrypt_return_unicode_string(self):
        message = "Salut la companie"
        encrypted = crypto.encrypt(message, "Client State", "Secret")
        decrypted = crypto.decrypt(encrypted, "Client State", "Secret")
        self.assertIsInstance(decrypted, text_type)
