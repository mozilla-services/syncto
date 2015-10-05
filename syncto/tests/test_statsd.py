import mock

from cliquet import statsd
from cliquet.cache.memory import Memory
from cliquet.tests.support import DummyRequest


from syncto import AUTHORIZATION_HEADER, CLIENT_STATE_HEADER
from syncto.authentication import build_sync_client
from syncto.tests.support import unittest

ENCRYPTED_CREDENTIALS = (
    'ada7bf44ae1f88bdb08a0ad4d8702419f77912f5ee4a7a06948a88993cd05d77b8'
    'e1cc01212db4b007102e7eaf2379afecc043324cc565337bba48c278052be99190'
    'a47b4040bf7cfa594414637ba50de16342cad902c8c249b9ae2af93e6675b52d55'
    '8ae157f98ff168deb719054917a44de115e43609c0bb2ce9a92a4cf1c2477ddddd'
    '38c625b92a0b5e9bd9a53247955479fbaa7a0a1bc3077f5ff71ef3b1c0decaac88'
)


@unittest.skipIf(not statsd.statsd_module, "statsd is not installed.")
class StatsdSyncClientTest(unittest.TestCase):

    def setUp(self):
        self.client = statsd.Client('localhost', 1234, 'prefix')

        p = mock.patch.object(self.client, '_client')
        self.mocked_client = p.start()
        self.addCleanup(p.stop)

        self.request = DummyRequest()
        self.request.registry.settings.update({
            'syncto.cache_hmac_secret': 'This is not a secret',
            'syncto.cache_credentials_ttl_seconds': 300})
        self.request.headers = {AUTHORIZATION_HEADER: 'Browserid 1234',
                                CLIENT_STATE_HEADER: '12345'}

        self.request.registry.cache = Memory()
        self.request.registry.cache.flush()
        self.request.registry.statsd = self.client

        self.credentials = {
            "api_endpoint": "http://example.org/",
            "uid": "123456",
            "hashalg": "sha256",
            "id": "mon-id",
            "key": "I am not a secure key"
        }

    def test_statsd_time_token_server_call(self):
        with mock.patch('requests.request'):
            self.mocked_client.timer()().return_value = self.credentials

            with mock.patch('syncto.authentication.SyncClient'):
                build_sync_client(self.request)
                self.mocked_client.timer.assert_any_call(
                    'tokenserver.tokenserverclient.get_hawk_credentials')

    def test_statsd_time_sync_client_calls(self):
        with mock.patch.object(
                self.request.registry.cache, 'get',
                return_value=ENCRYPTED_CREDENTIALS.encode('utf-8')):
            with mock.patch('requests.request'):
                build_sync_client(self.request)
                self.mocked_client.timer.assert_any_call(
                    'syncclient.start_time')
                self.mocked_client.timer.assert_any_call(
                    'syncclient.syncclient.auth')
                self.mocked_client.timer.assert_any_call(
                    'syncclient.syncclient.get_records')
                self.mocked_client.timer.assert_any_call(
                    'syncclient.syncclient.get_record')
                self.mocked_client.timer.assert_any_call(
                    'syncclient.syncclient.put_record')
                self.mocked_client.timer.assert_any_call(
                    'syncclient.syncclient.delete_record')
