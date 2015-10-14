import mock

from cliquet import statsd
from cliquet.cache.memory import Memory
from cliquet.tests.support import DummyRequest
from requests.exceptions import HTTPError

from syncto import AUTHORIZATION_HEADER, CLIENT_STATE_HEADER
from syncto.authentication import build_sync_client
from syncto.tests.support import unittest, ENCRYPTED_CREDENTIALS
from syncto.views import collection, record
from syncto.views.errors import response_error

COLLECTION_URL = "/buckets/syncto/collections/tabs/records"


class StatsdTestMixin(object):

    def setUp(self):
        self.client = statsd.Client('localhost', 1234, 'prefix')

        p = mock.patch.object(self.client, '_client')
        self.mocked_client = p.start()
        self.addCleanup(p.stop)

        self.request = DummyRequest()
        self.request.registry.settings.update({
            'cache_hmac_secret': 'This is not a secret',
            'cache_credentials_ttl_seconds': 300,
            'token_server_url': 'https://token.services.mozilla.com/'})
        self.request.headers = {AUTHORIZATION_HEADER: 'Browserid 1234',
                                CLIENT_STATE_HEADER: '12345'}
        self.request.response.headers = {'Content-Type': 'application/json'}

        self.request.registry.cache = Memory()
        self.request.registry.cache.flush()
        self.request.registry.statsd = self.client


@unittest.skipIf(not statsd.statsd_module, "statsd is not installed.")
class StatsdSyncClientTest(StatsdTestMixin, unittest.TestCase):

    def setUp(self):
        super(StatsdSyncClientTest, self).setUp()

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


@unittest.skipIf(not statsd.statsd_module, "statsd is not installed.")
class StatsdHTTPErrorStatusCodeTest(StatsdTestMixin, unittest.TestCase):

    def test_response_error_counts_500_in_statsd_and_in_sentry(self):
        response = mock.MagicMock()
        response.status_code = 500
        with mock.patch('syncto.views.errors.logger') as logger_mock:
            logger_mock.error.return_value = None
            error = HTTPError(response=response)
            response_error(error, self.request)
            self.mocked_client.incr.assert_called_with(
                "syncclient.status_code.500", count=1)
            logger_mock.error.assert_called_with(error, exc_info=True)

    def test_response_error_counts_304_in_statsd(self):
        response = mock.MagicMock()
        response.status_code = 304
        response_error(HTTPError(response=response), self.request)
        self.mocked_client.incr.assert_called_with(
            "syncclient.status_code.304", count=1)

    def test_response_error_counts_401_in_statsd(self):
        response = mock.MagicMock()
        response.status_code = 401
        try:
            raise HTTPError(response=response)
        except HTTPError as e:
            response_error(e, self.request)
        self.mocked_client.incr.assert_called_with(
            "syncclient.status_code.401", count=1)

    def test_response_error_counts_403_in_statsd(self):
        response = mock.MagicMock()
        response.status_code = 403
        try:
            raise HTTPError(response=response)
        except HTTPError as e:
            response_error(e, self.request)
        self.mocked_client.incr.assert_called_with(
            "syncclient.status_code.403", count=1)

    def test_response_error_counts_404_in_statsd(self):
        response = mock.MagicMock()
        response.status_code = 404
        try:
            raise HTTPError(response=response)
        except HTTPError as e:
            response_error(e, self.request)
        self.mocked_client.incr.assert_called_with(
            "syncclient.status_code.404", count=1)

    def test_response_error_counts_412_in_statsd(self):
        response = mock.MagicMock()
        response.status_code = 412
        response_error(HTTPError(response=response), self.request)
        self.mocked_client.incr.assert_called_with(
            "syncclient.status_code.412", count=1)


@unittest.skipIf(not statsd.statsd_module, "statsd is not installed.")
class StatsdSuccessStatusCodeTest(StatsdTestMixin, unittest.TestCase):

    def test_collection_get_counts_200_in_statsd(self):
        with mock.patch(
                'syncto.views.collection.build_sync_client') as build_mock:

            build_mock.return_value._authenticate.return_value = None
            build_mock.return_value.get_records.return_value = []

            self.request.matchdict['collection_name'] = 'history'
            collection.collection_get(self.request)

            self.mocked_client.incr.assert_called_with(
                "syncclient.status_code.200", count=1)

    def test_record_get_counts_200_in_statsd(self):
        with mock.patch(
                'syncto.views.record.build_sync_client') as build_mock:

            build_mock.return_value._authenticate.return_value = None
            build_mock.return_value.get_records.return_value = {}

            self.request.matchdict['collection_name'] = 'history'
            self.request.matchdict['record_id'] = '1234'
            record.record_get(self.request)

            self.mocked_client.incr.assert_called_with(
                "syncclient.status_code.200", count=1)

    def test_record_put_counts_200_in_statsd(self):
        with mock.patch(
                'syncto.views.record.build_sync_client') as build_mock:

            build_mock.return_value._authenticate.return_value = None
            build_mock.return_value.get_records.return_value = {}

            self.request.matchdict['collection_name'] = 'history'
            self.request.matchdict['record_id'] = '1234'
            self.request.validated['data'] = {}

            self.request.method = 'PUT'
            self.request.registry.settings['record_history_put_enabled'] = True

            record.record_put(self.request)

            self.mocked_client.incr.assert_called_with(
                "syncclient.status_code.200", count=1)

    def test_record_delete_counts_200_in_statsd(self):
        with mock.patch(
                'syncto.views.record.build_sync_client') as build_mock:

            build_mock.return_value._authenticate.return_value = None
            build_mock.return_value.get_records.return_value = {}

            self.request.matchdict['collection_name'] = 'history'
            self.request.matchdict['record_id'] = '1234'
            self.request.validated['data'] = {}

            self.request.method = 'DELETE'
            settings = self.request.registry.settings
            settings['record_history_delete_enabled'] = True

            record.record_delete(self.request)

            self.mocked_client.incr.assert_called_with(
                "syncclient.status_code.204", count=1)
