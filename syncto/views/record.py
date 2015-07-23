from pyramid import httpexceptions
from pyramid.security import NO_PERMISSION_REQUIRED, forget

from cliquet import Service
from cliquet.errors import http_error, ERRORS
from sync.client import SyncClient

from syncto.utils import base64_to_uuid4, uuid4_to_base64


record = Service(name='record',
                 description='Get the Firefox Sync Collection',
                 path=('/buckets/syncto/collections/'
                       '{collection_name}/records/{record_id}'),
                 cors_headers=('Last-Modified', 'ETag'))

AUTHORIZATION_HEADER = 'Authorization'
CLIENT_STATE_HEADER = 'X-Client-State'


@record.get(permission=NO_PERMISSION_REQUIRED)
def record_get(request):
    collection_name = request.matchdict['collection_name']
    record_id = request.matchdict['record_id']
    sync_id = uuid4_to_base64(record_id)

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
    record = sync_client.get_record(collection_name, sync_id)

    record['last_modified'] = int(record.pop('modified') * 1000)
    record['id'] = base64_to_uuid4(record.pop('id'))

    # Configure headers
    response_headers = sync_client.raw_resp.headers
    headers = request.response.headers

    last_modified = float(response_headers['X-Last-Modified'])
    headers['ETag'] = '"%s"' % int(last_modified * 1000)
    request.response.last_modified = last_modified

    return {'data': record}
