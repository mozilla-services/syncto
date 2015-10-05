from __future__ import unicode_literals
import nacl.secret
import re
from six import text_type

from syncto import crypto
from syncto.tests.support import unittest


class CryptoTest(unittest.TestCase):
    def test_get_nacl_secret_box_encode_client_state_if_text_type(self):
        box = crypto._get_nacl_secret_box("Client State", "HMAC secret")
        self.assertIsInstance(box, nacl.secret.SecretBox)

    def test_get_nacl_secret_box_accept_client_state_as_bytes(self):
        box = crypto._get_nacl_secret_box("Client State".encode('utf-8'),
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
