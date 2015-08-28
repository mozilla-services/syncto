from pyramid.security import NO_PERMISSION_REQUIRED

from cliquet import Service

from syncto.authentication import build_sync_client
from syncto.headers import convert_headers
from syncto.utils import base64_to_uuid4, uuid4_to_base64


record = Service(name='record',
                 description='Firefox Sync Collection Record service',
                 path=('/buckets/syncto/collections/'
                       '{collection_name}/records/{record_id}'),
                 cors_headers=('Last-Modified', 'ETag'))


@record.get(permission=NO_PERMISSION_REQUIRED)
def record_get(request):
    collection_name = request.matchdict['collection_name']
    record_id = request.matchdict['record_id']
    sync_id = uuid4_to_base64(record_id)

    sync_client = build_sync_client(request)
    record = sync_client.get_record(collection_name, sync_id)

    record['last_modified'] = int(record.pop('modified') * 1000)
    record['id'] = base64_to_uuid4(record.pop('id'))

    # Configure headers
    convert_headers(sync_client.raw_resp, request.response)

    return {'data': record}


@record.delete(permission=NO_PERMISSION_REQUIRED)
def record_delete(request):
    collection_name = request.matchdict['collection_name']
    record_id = request.matchdict['record_id']
    sync_id = uuid4_to_base64(record_id)

    sync_client = build_sync_client(request)
    sync_client.delete_record(collection_name, sync_id)

    request.response.status_code = 204
    return None
