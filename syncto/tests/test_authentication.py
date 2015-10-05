import mock

from pyramid.httpexceptions import HTTPUnauthorized
from cliquet.cache.memory import Memory
from cliquet.tests.support import DummyRequest

from syncto import AUTHORIZATION_HEADER, CLIENT_STATE_HEADER
from syncto.authentication import build_sync_client
from syncto.tests.support import unittest


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
