import mock
import json

from cliquet.cache.memory import Memory
from cliquet.tests.support import DummyRequest
from nacl.exceptions import CryptoError
from pyramid.httpexceptions import HTTPUnauthorized

from syncto import AUTHORIZATION_HEADER, CLIENT_STATE_HEADER
from syncto.authentication import build_sync_client, base64url_decode
from syncto.tests.support import unittest, ENCRYPTED_CREDENTIALS


class BuildSyncClientTest(unittest.TestCase):

    def setUp(self):
        self.request = DummyRequest()
        self.request.registry.settings.update({
            'cache_hmac_secret': 'This is not a secret',
            'cache_credentials_ttl_seconds': 300})

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

    def test_credentials_should_be_cached_encrypted(self):
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
        with mock.patch.object(
                self.request.registry.cache, 'get',
                return_value=ENCRYPTED_CREDENTIALS):
            with mock.patch('requests.request'):
                with mock.patch('syncto.authentication.decrypt',
                                return_value=json.dumps(self.credentials)) \
                        as mocked_decrypt:
                    build_sync_client(self.request)
                    mocked_decrypt.assert_called_with(ENCRYPTED_CREDENTIALS,
                                                      '12345',
                                                      'This is not a secret')

    def test_in_case_decryption_fails_it_should_raise(self):
        self.request.headers = {AUTHORIZATION_HEADER: 'Browserid 1234',
                                CLIENT_STATE_HEADER: '12345'}
        tempered_cache = ENCRYPTED_CREDENTIALS.replace('0', 'a')
        with mock.patch('syncto.authentication.TokenserverClient') as TSClient:
            TSClient.return_value.get_hawk_credentials.return_value = \
                self.credentials
            with mock.patch.object(
                    self.request.registry.cache, 'get',
                    return_value=tempered_cache):
                self.assertRaises(CryptoError, build_sync_client, self.request)

    def test_base64url_decode_raises_ValueError_in_case_of_problem(self):
        self.assertRaises(ValueError, base64url_decode, u'A')

    def test_uses_ttl_from_settings_if_assertion_is_in_old_format(self):
        # This assertion comes from PyBrowserID tests cases.
        # https://github.com/mozilla/PyBrowserID
        assertion = """
        eyJjZXJ0aWZpY2F0ZXMiOlsiZXlKaGJHY2lPaUpTVXpFeU9DSjkuZXlKcGMzTWlPaUppY
        205M2MyVnlhV1F1YjNKbklpd2laWGh3SWpveE16SXhPVFF4T1Rnek1EVXdMQ0p3ZFdKc2
        FXTXRhMlY1SWpwN0ltRnNaMjl5YVhSb2JTSTZJbEpUSWl3aWJpSTZJamd4TmpreE5UQTB
        OVGswTkRVek5EVTFPREF4TlRreU5Ea3hNemsyTkRFNE56RTJNVFUwTkRNNE5EWXdPREl6
        TXpBMU1USXlPRGN3TURRNE56TTFNREk1TURrek16a3lNRFkzTURFMU1qQTBORGd6TWpVM
        U56WXdOREE1TnpFeU9EYzNNVGswT1RVek1UQXdNVFEyTkRVek56TTJOakU0TlRVek5EY3
        hNakkxT0RreU16TTFPRFV4TWpZNU1EQXdOREF5TVRrMk9ERTBNRGtpTENKbElqb2lOalU
        xTXpjaWZTd2ljSEpwYm1OcGNHRnNJanA3SW1WdFlXbHNJam9pY25saGJrQnlabXN1YVdR
        dVlYVWlmWDAua19oaEtYMFRCVnUyX2szbV9uRDVOVWJfTktwX19PLTY1MW1CRUl3S1NZZ
        GlOenQwQm9WRkNEVEVueEhQTWJCVjJaejk0WDgtLVRjVXJidEV0MWV1S1dWdjMtNTFUOU
        xBZnV6SEhfekNCUXJVbmxkMVpXSmpBM185ZEhQeTMwZzRMSU9YZTJWWmd0T1Nva3MyZFE
        4ZDNvazlSUTJQME5ERzB1MDBnN3lGejE4Il0sImFzc2VydGlvbiI6ImV5SmhiR2NpT2lK
        U1V6WTBJbjAuZXlKbGVIQWlPakV6TWpFNU1qazBOelU0TWprc0ltRjFaQ0k2SW1oMGRIQ
        TZMeTl0ZVdaaGRtOXlhWFJsWW1WbGNpNXZjbWNpZlEuQWhnS2Q0eXM0S3FnSGJYcUNSS3
        hHdlluVmFJOUwtb2hYSHk0SVBVWDltXzI0TWdfYlU2aGRIMTNTNnFnQy1vSHBpS3BfTGl
        6cDRGRjlUclBjNjBTRXcifQ
        """.replace(" ", "").replace("\n", "").strip()
        self.request.headers = {AUTHORIZATION_HEADER: 'Browserid ' + assertion,
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
                    args, _ = tuple(mocked_set.call_args_list[-1])
                    ttl = args[-1]
                    self.assertEqual(int(ttl), 300)

    def test_uses_ttl_from_assertion_if_smaller_than_settings(self):
        assertion = """
        eyJhbGciOiJSUzI1NiJ9.eyJwdWJsaWMta2V5Ijp7ImFsZ29yaXRobSI6IkRTIiwiZyI6I
        jY3ZTU4NjQ2MGYzMzMyNjliNzlhZmJjZDA4MmYzNjk5NGMxNGNjZGMwYWQ5NWNhMmNmMWQ
        4MTZjMjVkZTQ5MmRiMTI2ZDkwOTc2ZmNmMWY3YWIxMmE4MTRkMTEwYzEzZWI0YmY1MjliM
        2M3ZmE3MDViYWVkZTcyZmI5ZTY5YmYzNzMzOTkwMjYzZDMwM2I4M2YyMGM4Nzg0OGI3YTg
        zMTg3ZWQzNjYwZTY0MThlOGY4YzAwNTE2ZWY5MGJlZmY0ODAyM2E1ZDc0NzllMjA1MGRiM
        2FlNjBhYWZkOWRkNGEyODk1NmNiNWVlNzRmMDA0NDc2MWQ4MTc1YmQ0NTYzOSIsInEiOiJ
        lMDc1YTgxMzEwNzAxZGFmNGE3M2E0MTRhYWJmNmNmZTRjZmI2M2UzIiwicCI6IjljYjFkZ
        jA4N2RjMjQ5YzEyZmRhOWFkYmY2YTE4MGQ0MDZmZTUwOGJjNjI3NzEyMGRkZDdmYzRhYjU
        xMThmYWY0ZjhmM2MyNTVmYWYwY2UyNGIzMjU5NWEwZmNkNjc1MTc0NmZiZDdmMzNjZWVlM
        TFhOWM2NTBjN2JkMDE3NTk1ZjBiOWMxOGY3NTEyMjg5MTI4YzQ1NjQzYTA3MjAxNGM1MGN
        jNWIxMDM4MDhkNmVmNTcwMWFiY2Q1ODAzMDgxYjIxNTIwNGI5OTIzNzNkYWIxZDVhMjdmM
        2NiMDFjNmY4NThkZDhkNzc3ZWZjZTgwNmRhYmI2YjgyNWMxYjU3ZTciLCJ5IjoiOTYyZWQ
        1ODE5NDcyMmNiMDQxNmE1M2E3OWQ2ZWEzOGIxYmQ2MmIxYzk2NWEwNGJmM2MzY2Q2MDQ3Y
        jVmZjBkMGFmZWEyYmE5ZjU0YjFkODE5M2UxN2FhZjVlYWE3NzUwMDBiMDVjZTQ2YmNmZTY
        wMzcyMTJkODI5YWFjYWRjNzFhMTA1MTMwNDk5ZGM2OWIzMzEwZTJkYzIxODAyYTQzNWFiY
        jU0M2IwOTFmY2U1NTVmYWRiNGQyZGNiZjVjN2MxNmQ5OTU0N2QwNWMwZDAwZDhkMGJmOTJ
        lMDE2M2UxNTRiYzQ0MmZhNTRjOGYwN2MxMjU4MzRlZDJhZDIyNmFiYiJ9LCJwcmluY2lwY
        WwiOnsiZW1haWwiOiI0NjY1NWQxMDQyNTU0OTYzOWFhZTI5N2M2ZmM2ZDYzMkBhcGkuYWN
        jb3VudHMuZmlyZWZveC5jb20ifSwiaWF0IjoxNDQ0MTIyNTczNTgwLCJleHAiOjE0NDQxM
        jQzODM1ODAsImZ4YS1nZW5lcmF0aW9uIjoxNDQ0MTIyNTA4ODM2LCJmeGEtbGFzdEF1dGh
        BdCI6MTQ0NDEyMjU4MiwiZnhhLXZlcmlmaWVkRW1haWwiOiJzeW5jdG9AcmVzdG1haWwub
        mV0IiwiaXNzIjoiYXBpLmFjY291bnRzLmZpcmVmb3guY29tIn0.39sRjyvQyEXgoWDHTzi
        J7LDfp8HqMyLIVXlCri0-SOSJq2QzKEdG0R3MKEdYMhH20dLKRqTqOmt1UiG1vw3XTUhHe
        5BOmjpQxMBRLoHSXWSIrfk0OCAPVdHIRVDOarNkaD7AYJ0ADdYMpx-EHov7N3tKVGOfURn
        _BwuM55dw7j6xeK_Qpy9iYRK59ApIlEFlxyWH4fAPvs45tThnJVwXjuBP1Bezt7O6SbLzv
        4lgZdDRdBrEnMA6YyLrJsV1_balKy9AQkT8Ye7lsHp9ysgdf6FiSvsvWOM_ZQaRy6V8lTq
        Ue9yTXyd5Ex5aJO62neLo-TZZ4beHNHd-XqBhkkb2bQ~eyJhbGciOiAiRFMxMjgifQ.eyJ
        hdWQiOiAiaHR0cHM6Ly90b2tlbi5zZXJ2aWNlcy5tb3ppbGxhLmNvbS8iLCAiZXhwIjogM
        TQ0NDEyNjE4MzAwMH0.i_0cKFEKNvRiGETGp8xNXH_JDEGsdhqguKGlcdCWeHr_EyUlUsh
        vnw""".replace(" ", "").replace("\n", "").strip()
        self.request.registry.settings.update({
            'syncto.cache_credentials_ttl_seconds': 3600})

        self.request.headers = {AUTHORIZATION_HEADER: 'Browserid ' + assertion,
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
                    args, _ = tuple(mocked_set.call_args_list[-1])
                    ttl = args[-1]
                    self.assertNotEqual(int(ttl), 3600)
