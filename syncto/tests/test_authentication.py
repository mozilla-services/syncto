import mock
import json

from pyramid.httpexceptions import HTTPUnauthorized
from cliquet.cache.memory import Memory
from cliquet.tests.support import DummyRequest

from syncto import AUTHORIZATION_HEADER, CLIENT_STATE_HEADER
from syncto.authentication import build_sync_client
from syncto.tests.support import unittest, ENCRYPTED_CREDENTIALS


class BuildSyncClientTest(unittest.TestCase):

    def setUp(self):
        self.request = DummyRequest()
        self.request.registry.settings.update({
            'syncto.cache_hmac_secret': 'This is not a secret',
            'syncto.cache_credentials_ttl_seconds': 300})

        self.request.registry.cache = Memory()

        self.credentials = {
            "api_endpoint": "http://example.org/",
            "uid": "123456",
            "hashalg": "sha256",
            "id": "mon-id",
            "key": "I am not a secure key"
        }

    def test_should_raise_if_authorization_header_is_missing(self):
        self.assertRaises(HTTPUnauthorized, build_sync_client, self.request)

    def test_should_raise_if_client_state_header_is_missing(self):
        self.request.headers = {AUTHORIZATION_HEADER: 'Browserid 1234'}
        self.assertRaises(HTTPUnauthorized, build_sync_client, self.request)

    def test_should_return_the_client_if_everything_is_fine(self):
        self.request.headers = {AUTHORIZATION_HEADER: 'Browserid 1234',
                                CLIENT_STATE_HEADER: '12345'}
        with mock.patch('syncto.authentication.TokenserverClient') as TSClient:
            TSClient.return_value.get_hawk_credentials.return_value = \
                self.credentials
            with mock.patch('syncto.authentication.SyncClient') as SyncClient:
                build_sync_client(self.request)
                TSClient.assert_called_with('1234', '12345')
                SyncClient.assert_called_with(**self.credentials)

    def test_should_cache_credentials_the_second_time(self):
        self.request.headers = {AUTHORIZATION_HEADER: 'Browserid 1234',
                                CLIENT_STATE_HEADER: '12345'}
        self.request.registry.cache.flush()
        with mock.patch('syncto.authentication.TokenserverClient') as TSClient:
            TSClient.return_value.get_hawk_credentials.return_value = \
                self.credentials
            with mock.patch('syncto.authentication.SyncClient') as SyncClient:
                # First call
                build_sync_client(self.request)
                SyncClient.assert_called_with(**self.credentials)
                # Second time
                build_sync_client(self.request)
                # TokenServerClient should have been called only once.
                TSClient.assert_called_once_with('1234', '12345')
                SyncClient.assert_called_with(**self.credentials)

    def test_should_cache_encrypted_credentials(self):
        self.request.headers = {AUTHORIZATION_HEADER: 'Browserid 1234',
                                CLIENT_STATE_HEADER: '12345'}
        self.request.registry.cache.flush()
        with mock.patch('syncto.authentication.TokenserverClient') as TSClient:
            TSClient.return_value.get_hawk_credentials.return_value = \
                self.credentials
            with mock.patch('syncto.authentication.encrypt',
                            return_value='encrypted'):
                with mock.patch.object(self.request.registry.cache, 'set') \
                        as mocked_set:
                    build_sync_client(self.request)
                    cache_key = ('credentials_636130e072155efd00d8e27196500'
                                 'd29110fb2e8e93bcedb2a30e0aa0e5ccf61')
                    mocked_set.assert_called_with(cache_key,
                                                  'encrypted', 300)

    def test_should_decrypt_credentials(self):
        self.request.headers = {AUTHORIZATION_HEADER: 'Browserid 1234',
                                CLIENT_STATE_HEADER: '12345'}
        encrypted_credentials = ENCRYPTED_CREDENTIALS.encode('utf-8')
        with mock.patch.object(
                self.request.registry.cache, 'get',
                return_value=encrypted_credentials):
            with mock.patch('requests.request'):
                with mock.patch('syncto.authentication.decrypt',
                                return_value=json.dumps(self.credentials)) \
                        as mocked_decrypt:
                    build_sync_client(self.request)
                    mocked_decrypt.assert_called_with(encrypted_credentials,
                                                      '12345',
                                                      'This is not a secret')
