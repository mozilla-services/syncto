from pyramid import httpexceptions
from pyramid.security import NO_PERMISSION_REQUIRED, forget

from cliquet import Service
from cliquet.errors import http_error, ERRORS
from sync.client import SyncClient


history = Service(name='history',
                  description='Get the Firefox Sync History',
                  path='/history')


@history.get(permission=NO_PERMISSION_REQUIRED)
def history_get(request):
    # Get the BID assertion
    if 'Backend-Authorization' not in request.headers:
        error_msg = "Provide a Backend-Authorization BID assertion header."
        response = http_error(httpexceptions.HTTPUnauthorized(),
                              errno=ERRORS.MISSING_AUTH_TOKEN,
                              message=error_msg)
        response.headers.extend(forget(request))
        return response

    if 'Backend-Client-State' not in request.headers:
        error_msg = "Provide the tokenserver Client-State header."
        response = http_error(httpexceptions.HTTPUnauthorized(),
                              errno=ERRORS.MISSING_AUTH_TOKEN,
                              message=error_msg)
        response.headers.extend(forget(request))
        return response

    bid_assertion = request.headers['Backend-Authorization']
    client_state = request.headers['Backend-Client-State']
    sync_client = SyncClient(bid_assertion, client_state)
    records = sync_client.get_records('history', full=True)

    return {'data': records}
