import mock
import os
from contextlib import contextmanager
from uuid import uuid4

from cliquet.errors import ERRORS
from cliquet.tests.support import FormattedErrorMixin
from requests.exceptions import HTTPError, ConnectionError

from syncto import __version__
from syncto import AUTHORIZATION_HEADER, CLIENT_STATE_HEADER
from syncto import main as testapp
from syncto.heartbeat import ping_sync_cluster

from .support import BaseWebTest, unittest

HERE = os.path.abspath(os.path.dirname(__file__))

MANDATORY_SETTINGS = {
    'cache_hmac_secret': 'This is not a secret'
}

COLLECTION_URL = "/buckets/syncto/collections/tabs/records"
RECORD_URL = "/buckets/syncto/collections/tabs/records/%s" % uuid4()

RECORD_EXAMPLE = {
    "data": {
        "payload": "abcd"
    }
}

_USER_AGENT = 'Syncto/%s' % __version__
_DEFAULT_SYNC_HEADERS = {'User-Agent': _USER_AGENT}


class SettingsMissingTest(unittest.TestCase):

    def test_syncto_cache_hmac_secret_missing(self):
        settings = MANDATORY_SETTINGS.copy()
        # Remove the mandatory setting we want to test
        del settings['cache_hmac_secret']
        self.assertRaises(ValueError, testapp, {}, **settings)

    def test_syncto_certificate_ca_bundle_file_not_found(self):
        settings = MANDATORY_SETTINGS.copy()
        # Remove the mandatory setting we want to test
        settings['certificate_ca_bundle'] = 'foobar.crt'
        self.assertRaises(ValueError, testapp, {}, **settings)

    def test_syncto_certificate_ca_bundle_relative_file_found(self):
        settings = MANDATORY_SETTINGS.copy()
        # Remove the mandatory setting we want to test
        digicert_ca_bundle = 'certificates/DigiCert.Global-Root-CA.crt'
        settings['certificate_ca_bundle'] = digicert_ca_bundle
        app = testapp({}, **settings)
        self.assertEqual(app.registry.settings['certificate_ca_bundle'],
                         os.path.normpath(os.path.join(
                             HERE, '..', '..', digicert_ca_bundle)))


class KintoJsCompatTest(BaseWebTest, unittest.TestCase):

    def test_public_settings_are_shown_in_view_prefixed_with_cliquet(self):
        response = self.app.get('/')
        settings = response.json['settings']
        self.assertEqual(settings['batch_max_requests'], 25)
        self.assertEqual(settings['cliquet.batch_max_requests'], 25)


class ErrorsTest(FormattedErrorMixin, BaseWebTest, unittest.TestCase):

    def test_authorization_header_is_required_for_collection(self):
        resp = self.app.get(COLLECTION_URL, headers=self.headers, status=401)

        self.assertFormattedError(
            resp, 401, ERRORS.MISSING_AUTH_TOKEN, "Unauthorized",
            "Provide a BID assertion %s header." % AUTHORIZATION_HEADER)

    def test_client_state_header_is_required_for_collection(self):
        headers = self.headers.copy()
        headers['Authorization'] = "BrowserID abcd"
        resp = self.app.get(COLLECTION_URL, headers=headers, status=401)

        self.assertFormattedError(
            resp, 401, ERRORS.MISSING_AUTH_TOKEN, "Unauthorized",
            "Provide the tokenserver %s header." % CLIENT_STATE_HEADER)

    def test_authorization_header_is_required_for_records(self):
        resp = self.app.get(RECORD_URL, headers=self.headers, status=401)

        self.assertFormattedError(
            resp, 401, ERRORS.MISSING_AUTH_TOKEN, "Unauthorized",
            "Provide a BID assertion %s header." % AUTHORIZATION_HEADER)

    def test_client_state_header_is_required_for_records(self):
        headers = self.headers.copy()
        headers['Authorization'] = "BrowserID abcd"
        resp = self.app.get(RECORD_URL, headers=headers, status=401)

        self.assertFormattedError(
            resp, 401, ERRORS.MISSING_AUTH_TOKEN, "Unauthorized",
            "Provide the tokenserver %s header." % CLIENT_STATE_HEADER)

    def test_404_endpoint_returns_cors_headers(self):
        headers = self.headers.copy()
        headers['Origin'] = 'notmyidea.org'
        response = self.app.get('/unknown',
                                headers=headers,
                                status=404)
        self.assertEqual(response.headers['Access-Control-Allow-Origin'],
                         'notmyidea.org')

    @contextmanager
    def patched_client(self, path, status=401, reason="Unauthorized"):
        error = HTTPError()
        error.response = mock.MagicMock()
        error.response.status_code = status
        error.response.reason = reason
        error.response.text = ('{"status": "invalid-credentials", '
                               '"errors": [{"location": "body", '
                               '"name": "", '
                               '"description": "Unauthorized"}]}')
        patch = mock.patch(path, side_effect=error)
        try:
            yield patch.start()
        finally:
            patch.stop()

    def test_bad_client_state_header_raise_a_401(self):
        headers = self.headers.copy()
        headers['Authorization'] = "BrowserID valid-browser-id-assertion"
        headers['X-Client-State'] = "NonSense"
        with self.patched_client("syncto.authentication.TokenserverClient"):
            resp = self.app.get(COLLECTION_URL, headers=headers, status=401)

        self.assertFormattedError(
            resp, 401, ERRORS.INVALID_AUTH_TOKEN, "Unauthorized",
            '401 Unauthorized: {"status": "invalid-credentials"')

    def test_error_with_syncclient_server_raise_a_503(self):
        headers = self.headers.copy()
        headers['Authorization'] = "BrowserID valid-browser-id-assertion"
        headers['X-Client-State'] = "ValidClientState"
        with self.patched_client("syncto.authentication.TokenserverClient",
                                 503, "Service Unavailable"):
            resp = self.app.get(COLLECTION_URL, headers=headers, status=503)

        self.assertFormattedError(
            resp, 503, ERRORS.BACKEND, "Service Unavailable", "retry later")

    def test_error_with_syncclient_server_request(self):
        headers = self.headers.copy()
        headers['Authorization'] = "BrowserID valid-browser-id-assertion"
        headers['X-Client-State'] = "ValidClientState"
        with mock.patch("syncto.authentication.TokenserverClient",
                        side_effect=ConnectionError):
            resp = self.app.get(COLLECTION_URL, headers=headers, status=503)

            error_msg = ("Unable to reach the service. Check your "
                         "internet connection or firewall configuration.")

        self.assertFormattedError(
            resp, 503, ERRORS.BACKEND, "Service Unavailable", error_msg)


class BaseViewTest(BaseWebTest, unittest.TestCase):
    patch_authent_for = 'record'

    def setUp(self):
        super(BaseViewTest, self).setUp()

        self.headers.update({
            AUTHORIZATION_HEADER: "BrowserID abcd",
            CLIENT_STATE_HEADER: "1234",
            'Origin': 'http://localhost:8000'
        })

        last_modified = 14377478425.69

        p = mock.patch("syncto.views.%s.build_sync_client" %
                       self.patch_authent_for)
        self.sync_client = p.start()
        self.sync_client.return_value._authenticate.return_value = None
        self.sync_client.return_value.get_records.return_value = [{
            "id": "Y_-5-LEeQBuh60IT0MyWEQ",
            "modified": last_modified
        }]
        headers = {}
        headers['X-Last-Modified'] = '%s' % last_modified
        headers['X-Weave-Records'] = '1'
        headers['X-Weave-Next-Offset'] = '12345'
        headers['X-Weave-Quota-Remaining'] = '125'
        self.sync_client.return_value.raw_resp.headers = headers
        self.sync_client.return_value.put_record.return_value = last_modified

        self.addCleanup(p.stop)

    def get_app_settings(self, extra=None):
        settings = super(BaseViewTest, self).get_app_settings(extra)
        settings['record_tabs_put_enabled'] = True
        settings['record_tabs_delete_enabled'] = True
        return settings


class CollectionTest(FormattedErrorMixin, BaseViewTest):

    patch_authent_for = 'collection'

    def test_collection_handle_cors_headers(self):
        resp = self.app.get(COLLECTION_URL,
                            headers=self.headers, status=200)
        self.assertIn('Access-Control-Allow-Origin', resp.headers)

    def test_collection_handle_cache_control_headers(self):
        resp = self.app.get(COLLECTION_URL,
                            headers=self.headers, status=200)
        self.assertIn('Cache-Control', resp.headers)

    def test_original_user_agent_is_passed_to_sync(self):
        headers = self.headers.copy()
        headers['User-Agent'] = 'HTTPie/0.9.2'
        self.app.get(COLLECTION_URL, headers=headers)

        expected = '%s (on behalf of HTTPie/0.9.2)' % _USER_AGENT
        self.sync_client.return_value.get_records.assert_called_with(
            "tabs", full=True, headers={'User-Agent': expected})

    def test_collection_handle_since_parameter(self):
        self.app.get(COLLECTION_URL,
                     params={'_since': '14377478425700',
                             '_sort': 'newest'},
                     headers=self.headers, status=200)

        self.sync_client.return_value.get_records.assert_called_with(
            "tabs", full=True, newer='14377478425.70', sort='newest',
            headers=_DEFAULT_SYNC_HEADERS)

    def test_collection_handles_if_none_match_headers(self):
        headers = self.headers.copy()
        headers['If-None-Match'] = '"14377478425700"'
        self.app.get(COLLECTION_URL,
                     params={'_since': '14377478425700',
                             '_sort': 'newest'},
                     headers=headers, status=200)

        expected = {'X-If-Modified-Since': '14377478425.70'}
        expected.update(_DEFAULT_SYNC_HEADERS)
        self.sync_client.return_value.get_records.assert_called_with(
            "tabs", full=True, newer='14377478425.70', sort='newest',
            headers=expected)

    def test_collection_handle_if_match_headers(self):
        headers = self.headers.copy()
        headers['If-Match'] = '"14377478425700"'
        self.app.get(COLLECTION_URL,
                     params={'_since': '14377478425700',
                             '_sort': 'newest'},
                     headers=headers, status=200)

        expected = {'X-If-Unmodified-Since': '14377478425.70'}
        expected.update(_DEFAULT_SYNC_HEADERS)
        self.sync_client.return_value.get_records.assert_called_with(
            "tabs", full=True, newer='14377478425.70', sort='newest',
            headers=expected)

    def test_collection_raises_on_wrong_if_none_match_header_value(self):
        headers = self.headers.copy()
        headers['If-None-Match'] = 'abc'
        resp = self.app.get(COLLECTION_URL, headers=headers, status=400)

        self.assertFormattedError(
            resp, 400, ERRORS.INVALID_PARAMETERS, "Invalid parameters",
            "headers: Invalid value for If-None-Match")

    def test_collection_raises_on_wrong_if_match_header_value(self):
        headers = self.headers.copy()
        headers['If-Match'] = '42'
        resp = self.app.get(COLLECTION_URL, headers=headers, status=400)

        self.assertFormattedError(
            resp, 400, ERRORS.INVALID_PARAMETERS, "Invalid parameters",
            "headers: Invalid value for If-Match")

    def test_collection_raises_if_since_parameter_is_not_a_number(self):
        resp = self.app.get(COLLECTION_URL,
                            params={'_since': 'not-a-number'},
                            headers=self.headers, status=400)

        self.assertFormattedError(
            resp, 400, ERRORS.INVALID_PARAMETERS, "Invalid parameters",
            "_since should be a number.")

    def test_collection_handle_limit_and_token_parameters(self):
        self.app.get(COLLECTION_URL,
                     params={'_limit': '2', '_token': '12345',
                             '_sort': 'index'},
                     headers=self.headers, status=200)
        self.sync_client.return_value.get_records.assert_called_with(
            "tabs", full=True, limit='2', offset='12345', sort='index',
            headers=_DEFAULT_SYNC_HEADERS)

    def test_collection_handles_oldest_sort(self):
        self.app.get(COLLECTION_URL,
                     params={'_sort': 'oldest'},
                     headers=self.headers, status=200)
        self.sync_client.return_value.get_records.assert_called_with(
            "tabs", full=True, sort='oldest', headers=_DEFAULT_SYNC_HEADERS)

    def test_collection_raises_with_invalid_sort_parameter(self):
        resp = self.app.get(COLLECTION_URL,
                            params={'_sort': 'unknown'},
                            headers=self.headers, status=400)

        self.assertFormattedError(
            resp, 400, ERRORS.INVALID_PARAMETERS, "Invalid parameters",
            "_sort should be one of ('-last_modified', 'newest', "
            "'-sortindex', 'index', 'last_modified', 'oldest')")

    def test_collection_can_validate_a_list_of_specified_ids(self):
        self.app.get(COLLECTION_URL,
                     params={'in_ids': '123,456,789'},
                     headers=self.headers, status=200)

    def test_collection_returns_empty_list(self):
        self.sync_client.return_value.get_records.return_value = []
        resp = self.app.get(COLLECTION_URL,
                            headers=self.headers, status=200)
        self.assertEquals(len(resp.json['data']), 0)

    def test_collection_correctly_converts_sync_headers(self):
        resp = self.app.get(COLLECTION_URL,
                            headers=self.headers, status=200)
        self.assertIn('Total-Records', resp.headers)
        self.assertIn('Next-Page', resp.headers)
        self.assertIn('Quota-Remaining', resp.headers)
        self.assertEquals(resp.headers['Total-Records'], '1')
        next_page = 'http://localhost/v1' + COLLECTION_URL + '?_token=12345'
        self.assertEquals(resp.headers['Next-Page'], next_page)
        self.assertEquals(resp.headers['Quota-Remaining'], '125')

    def test_collection_does_not_return_Total_Records_when_paginating(self):
        resp = self.app.get(COLLECTION_URL+'?_limit=2',
                            headers=self.headers, status=200)
        self.assertNotIn('Total-Records', resp.headers)
        self.assertIn('Next-Page', resp.headers)

    def test_collection_return_a_307_in_case_of_not_modified_resource(self):
        response = mock.MagicMock()
        response.status_code = 304
        response.reason = "Not Modified"
        response.url = "http://www.example.com/"
        self.sync_client.return_value.get_records.side_effect = HTTPError(
            response=response)
        resp = self.app.get(COLLECTION_URL, headers=self.headers, status=304)
        self.assertEqual(resp.body, b'')

    def test_collection_correctly_generate_next_page_header(self):
        resp = self.app.get(COLLECTION_URL+'?_limit=2&sort=index',
                            headers=self.headers, status=200)
        self.assertIn('Next-Page', resp.headers)
        next_page = ('http://localhost/v1' + COLLECTION_URL +
                     '?_limit=2&sort=index&_token=12345')
        self.assertEquals(resp.headers['Next-Page'], next_page)


class RecordTest(BaseViewTest):

    def test_record_handle_cors_headers(self):
        resp = self.app.get(RECORD_URL, headers=self.headers, status=200)
        self.assertIn('Access-Control-Allow-Origin', resp.headers)

    def test_record_handle_cache_control_headers(self):
        resp = self.app.get(RECORD_URL, headers=self.headers, status=200)
        self.assertIn('Cache-Control', resp.headers)

    def test_can_delete_record(self):
        self.sync_client.return_value.delete_record.return_value = None
        self.app.delete(RECORD_URL, headers=self.headers, status=204)

    def test_can_delete_record_handles_if_match_headers(self):
        self.sync_client.return_value.delete_record.return_value = None

        headers = self.headers.copy()
        headers['If-Match'] = '"14377478425700"'
        self.app.delete(RECORD_URL, headers=headers, status=204)

        expected = {'X-If-Unmodified-Since': '14377478425.70'}
        expected.update(_DEFAULT_SYNC_HEADERS)
        self.sync_client.return_value.delete_record.assert_called_with(
            "tabs", RECORD_URL.split('/')[-1],
            headers=expected)

    def test_delete_return_a_503_in_case_of_unknown_error(self):
        response = mock.MagicMock()
        response.status_code = 500
        self.sync_client.return_value.delete_record.side_effect = HTTPError(
            response=response)
        self.app.delete(RECORD_URL, headers=self.headers, status=503)

    def test_delete_return_a_400_in_case_of_bad_request(self):
        response = mock.MagicMock()
        response.status_code = 400
        self.sync_client.return_value.delete_record.side_effect = HTTPError(
            response=response)
        self.app.delete(RECORD_URL, headers=self.headers, status=400)

    def test_delete_return_a_403_in_case_of_forbidden_resource(self):
        response = mock.MagicMock()
        response.status_code = 403
        self.sync_client.return_value.delete_record.side_effect = HTTPError(
            response=response)
        self.app.delete(RECORD_URL, headers=self.headers, status=403)

    def test_delete_return_a_404_in_case_of_unknown_resource(self):
        response = mock.MagicMock()
        response.status_code = 404
        self.sync_client.return_value.delete_record.side_effect = HTTPError(
            response=response)
        self.app.delete(RECORD_URL, headers=self.headers, status=404)

    def test_can_put_valid_record(self):
        self.app.put_json(RECORD_URL, RECORD_EXAMPLE,
                          headers=self.headers, status=200)

    def test_put_record_handles_if_none_match_headers(self):
        headers = self.headers.copy()
        headers['If-None-Match'] = '*'

        self.app.put_json(RECORD_URL, RECORD_EXAMPLE,
                          headers=headers, status=200)

        expected = {'X-If-Unmodified-Since': 0}
        expected.update(_DEFAULT_SYNC_HEADERS)
        put_record_arg = self.sync_client.return_value.put_record.mock_calls[0]
        self.assertDictEqual(put_record_arg[2]['headers'], expected)

    def test_412_error_is_forwared_in_batch(self):
        request = {
            'method': 'PUT',
            'path': RECORD_URL,
            'body': RECORD_EXAMPLE,
            'headers': self.headers
        }
        body = {'requests': [request, request]}

        self.sync_client.return_value.put_record.side_effect = [
            mock.MagicMock(status_code=201),
            HTTPError(response=mock.MagicMock(status_code=412))
        ]

        resp = self.app.post_json('/batch', body, status=200)
        self.assertEqual(resp.json['responses'][0]['status'], 200)
        self.assertEqual(resp.json['responses'][1]['status'], 412)

    def test_put_record_reject_invalid_record(self):
        invalid = {"payload": "foobar"}
        self.app.put_json(RECORD_URL, invalid, headers=self.headers,
                          status=400)

    def test_put_return_a_503_in_case_of_unknown_error(self):
        response = mock.MagicMock()
        response.status_code = 500
        self.sync_client.return_value.put_record.side_effect = HTTPError(
            response=response)
        self.app.put_json(RECORD_URL, RECORD_EXAMPLE,
                          headers=self.headers, status=503)

    def test_bad_request_returns_alert_and_backoff_response_headers(self):
        response = mock.MagicMock()
        response.status_code = 400
        alert = ('{"code": "hard-eol", "message": "Bla", '
                 '"url": "http://example.com"}')
        response.headers = {'X-Weave-Alert': alert, 'X-Weave-Backoff': '3600'}
        self.sync_client.return_value.put_record.side_effect = HTTPError(
            response=response)
        resp = self.app.put_json(RECORD_URL, RECORD_EXAMPLE,
                                 headers=self.headers, status=400)
        self.assertIn('Alert', resp.headers)
        self.assertEqual(resp.headers['Alert'], alert)
        self.assertIn('Backoff', resp.headers)
        self.assertEqual(resp.headers['Backoff'], '3600')

    def test_put_return_a_403_in_case_of_forbidden_resource(self):
        response = mock.MagicMock()
        response.status_code = 403
        self.sync_client.return_value.put_record.side_effect = HTTPError(
            response=response)
        self.app.put_json(RECORD_URL, RECORD_EXAMPLE,
                          headers=self.headers, status=403)

    def test_put_return_a_404_in_case_of_unknown_resource(self):
        response = mock.MagicMock()
        response.status_code = 404
        self.sync_client.return_value.put_record.side_effect = HTTPError(
            response=response)
        self.app.put_json(RECORD_URL, RECORD_EXAMPLE,
                          headers=self.headers, status=404)

    def test_put_return_a_412_in_case_of_failed_precondition_resource(self):
        response = mock.MagicMock()
        response.status_code = 412
        self.sync_client.return_value.put_record.side_effect = HTTPError(
            response=response)
        self.app.put_json(RECORD_URL, RECORD_EXAMPLE,
                          headers=self.headers, status=412)

    def test_get_return_a_307_in_case_of_not_modified_resource(self):
        response = mock.MagicMock()
        response.status_code = 304
        self.sync_client.return_value.get_record.side_effect = HTTPError(
            response=response)
        resp = self.app.get(RECORD_URL, headers=self.headers, status=304)
        self.assertEqual(resp.body, b'')


class WriteSafeguardTest(FormattedErrorMixin, BaseViewTest):
    def test_record_put_is_disabled_by_default(self):
        url = RECORD_URL.replace('tabs', 'meta')
        self.app.put_json(url, RECORD_EXAMPLE,
                          headers=self.headers, status=405)

    def test_record_delete_is_disabled_by_default(self):
        url = RECORD_URL.replace('tabs', 'meta')
        self.app.delete(url, headers=self.headers, status=405)

    def test_message_provides_details(self):
        url = RECORD_URL.replace('tabs', 'meta')
        resp = self.app.put_json(url, RECORD_EXAMPLE,
                                 headers=self.headers, status=405)
        self.assertFormattedError(
            resp, 405, ERRORS.METHOD_NOT_ALLOWED, 'Method Not Allowed',
            'Endpoint disabled for this collection in configuration.')


class HeartBeatTest(unittest.TestCase):

    def test_heartbeat_return_false_if_token_server_outofservice(self):
        with mock.patch('syncto.heartbeat.requests.get') as mocked_request:
            mocked_request.return_value.raise_for_status.side_effect = (
                HTTPError())
            request = mock.MagicMock()
            request.registry.settings = {
                'token_server_url': 'https://example.com',
                'token_server_heartbeat_timeout_seconds': 5
            }
            self.assertFalse(ping_sync_cluster(request))
            mocked_request.assert_called_with(
                'https://example.com/__heartbeat__', timeout=5)

    def test_heartbeat_return_true_if_token_server_is_working(self):
        with mock.patch('syncto.heartbeat.requests.get') as mocked_request:
            mocked_request.return_value.raise_for_status.return_value = None
            request = mock.MagicMock()
            request.registry.settings = {
                'token_server_url': 'https://example.com',
                'token_server_heartbeat_timeout_seconds': 5
            }
            self.assertTrue(ping_sync_cluster(request))
            mocked_request.assert_called_with(
                'https://example.com/__heartbeat__', timeout=5)
