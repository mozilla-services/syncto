import mock
from uuid import uuid4

from cliquet.errors import ERRORS
from cliquet.tests.support import FormattedErrorMixin

from syncto import AUTHORIZATION_HEADER, CLIENT_STATE_HEADER

from .support import BaseWebTest, unittest


COLLECTION_URL = "/buckets/syncto/collections/{collection_id}/records"
RECORD_URL = "/buckets/syncto/collections/{collection_id}/records/{record_id}"


class FunctionalTest(FormattedErrorMixin, BaseWebTest, unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(FunctionalTest, self).__init__(*args, **kwargs)
        self.collection_url = COLLECTION_URL.format(collection_id="tabs")
        self.record_url = RECORD_URL.format(collection_id="tabs",
                                            record_id=uuid4())

    def test_authorization_header_is_required_for_collection(self):
        resp = self.app.get(
            self.collection_url.format(collection_id="tabs"),
            headers=self.headers, status=401)

        self.assertFormattedError(
            resp, 401, ERRORS.MISSING_AUTH_TOKEN, "Unauthorized",
            "Provide a BID assertion %s header." % AUTHORIZATION_HEADER)

    def test_client_state_header_is_required_for_collection(self):
        headers = self.headers.copy()
        headers['Authorization'] = "BrowserID abcd"
        resp = self.app.get(
            self.collection_url.format(collection_id="tabs"),
            headers=headers, status=401)

        self.assertFormattedError(
            resp, 401, ERRORS.MISSING_AUTH_TOKEN, "Unauthorized",
            "Provide the tokenserver %s header." % CLIENT_STATE_HEADER)

    def test_authorization_header_is_required_for_records(self):
        resp = self.app.get(
            self.record_url.format(collection_id="tabs"),
            headers=self.headers, status=401)

        self.assertFormattedError(
            resp, 401, ERRORS.MISSING_AUTH_TOKEN, "Unauthorized",
            "Provide a BID assertion %s header." % AUTHORIZATION_HEADER)

    def test_client_state_header_is_required_for_records(self):
        headers = self.headers.copy()
        headers['Authorization'] = "BrowserID abcd"
        resp = self.app.get(
            self.record_url.format(collection_id="tabs"),
            headers=headers, status=401)

        self.assertFormattedError(
            resp, 401, ERRORS.MISSING_AUTH_TOKEN, "Unauthorized",
            "Provide the tokenserver %s header." % CLIENT_STATE_HEADER)

    def test_collection_handle_cors_headers(self):
        headers = self.headers.copy()
        headers.update({
            AUTHORIZATION_HEADER: "BrowserID abcd",
            CLIENT_STATE_HEADER: "1234",
            'Origin': 'http://localhost:8000'
        })

        with mock.patch("syncto.views.record.SyncClient") as SyncClient:
            SyncClient.return_value._authenticate.return_value = None
            SyncClient.return_value.get_record.return_value = {
                "id": "Y_-5-LEeQBuh60IT0MyWEQ",
                "modified": 14377478425.69
            }

            resp = self.app.get(self.record_url,
                                headers=headers, status=200)
            self.assertIn('Access-Control-Allow-Origin', resp.headers)
