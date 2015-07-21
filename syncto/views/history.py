from pyramid import httpexceptions
from pyramid.security import NO_PERMISSION_REQUIRED, forget

from cliquet import Service
from cliquet.errors import http_error, ERRORS
from sync.client import SyncClient


history = Service(name='history',
                  description='Get the Firefox Sync History',
                  path='/history')

AUTHORIZATION_HEADER = 'Authorization'
CLIENT_STATE_HEADER = 'X-Client-State'


@history.get(permission=NO_PERMISSION_REQUIRED)
def history_get(request):
    # Get the BID assertion
    if AUTHORIZATION_HEADER not in request.headers or \
       not request.headers[AUTHORIZATION_HEADER].lower() \
                                                .startswith("browserid"):
        error_msg = "Provide an Authorization BID assertion header."
        response = http_error(httpexceptions.HTTPUnauthorized(),
                              errno=ERRORS.MISSING_AUTH_TOKEN,
                              message=error_msg)
        response.headers.extend(forget(request))
        return response

    if CLIENT_STATE_HEADER not in request.headers:
        error_msg = "Provide the tokenserver Client-State header."
        response = http_error(httpexceptions.HTTPUnauthorized(),
                              errno=ERRORS.MISSING_AUTH_TOKEN,
                              message=error_msg)
        response.headers.extend(forget(request))
        return response

    authorization_header = request.headers[AUTHORIZATION_HEADER]

    bid_assertion = authorization_header.split(" ", 1)[1]
    client_state = request.headers[CLIENT_STATE_HEADER]
    sync_client = SyncClient(bid_assertion, client_state)
    records = sync_client.get_records('history', full=True)

    return {'data': records}
