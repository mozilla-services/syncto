from pyramid import httpexceptions
from pyramid.security import forget
from requests.exceptions import HTTPError

from cliquet.errors import http_error, ERRORS
from cliquet.views.errors import service_unavailable
from sync.client import SyncClient

from syncto import AUTHORIZATION_HEADER, CLIENT_STATE_HEADER


def build_sync_client(request):
    # Get the BID assertion
    is_authorization_defined = AUTHORIZATION_HEADER in request.headers
    starts_with_browser_id = False
    if is_authorization_defined:
        authorization = request.headers[AUTHORIZATION_HEADER].lower()
        starts_with_browser_id = authorization.startswith("browserid")

    if not is_authorization_defined or not starts_with_browser_id:
        error_msg = "Provide a BID assertion %s header." % (
            AUTHORIZATION_HEADER)
        response = http_error(httpexceptions.HTTPUnauthorized(),
                              errno=ERRORS.MISSING_AUTH_TOKEN,
                              message=error_msg)
        response.headers.extend(forget(request))
        raise response

    is_client_state_defined = CLIENT_STATE_HEADER in request.headers
    if not is_client_state_defined:
        error_msg = "Provide the tokenserver %s header." % (
            CLIENT_STATE_HEADER)
        response = http_error(httpexceptions.HTTPUnauthorized(),
                              errno=ERRORS.MISSING_AUTH_TOKEN,
                              message=error_msg)
        response.headers.extend(forget(request))
        raise response

    authorization_header = request.headers[AUTHORIZATION_HEADER]

    bid_assertion = authorization_header.split(" ", 1)[1]
    client_state = request.headers[CLIENT_STATE_HEADER]
    try:
        sync_client = SyncClient(bid_assertion, client_state)
    except HTTPError as e:
        if e.response.status_code in (400, 401):
            message = '%s %s: %s' % (e.response.status_code,
                                     e.response.reason,
                                     e.response.text)
            response = http_error(httpexceptions.HTTPUnauthorized(),
                                  errno=ERRORS.INVALID_AUTH_TOKEN,
                                  message=message)
            # Forget the current user credentials.
            response.headers.extend(forget(request))
            raise response
        else:
            raise service_unavailable(e, request)
    return sync_client
