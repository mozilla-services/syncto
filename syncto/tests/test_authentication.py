import mock
from .support import unittest

from pyramid.httpexceptions import HTTPUnauthorized
from cliquet.tests.support import DummyRequest

from syncto import AUTHORIZATION_HEADER, CLIENT_STATE_HEADER
from syncto.authentication import build_sync_client


class BuildSyncClientTest(unittest.TestCase):

    def setUp(self):
        self.request = DummyRequest()

    def test_should_raise_if_authorization_header_is_missing(self):
        self.assertRaises(HTTPUnauthorized, build_sync_client, self.request)

    def test_should_raise_if_client_state_header_is_missing(self):
        self.request.headers = {AUTHORIZATION_HEADER: 'Browserid 1234'}
        self.assertRaises(HTTPUnauthorized, build_sync_client, self.request)

    def test_should_return_the_client_if_everything_is_fine(self):
        self.request.headers = {AUTHORIZATION_HEADER: 'Browserid 1234',
                                CLIENT_STATE_HEADER: '12345'}
        with mock.patch('syncto.authentication.SyncClient') as SyncClient:
            build_sync_client(self.request)
            SyncClient.assert_called_with('1234', '12345')
