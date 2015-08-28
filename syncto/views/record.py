import re

from cliquet import Service, schema
from pyramid.security import NO_PERMISSION_REQUIRED

from syncto.authentication import build_sync_client
from syncto.headers import convert_headers
from syncto.utils import base64_to_uuid4, uuid4_to_base64


SYNC_ID_FORMAT = re.compile(r'^[a-zA-Z0-9_-]{12}$')  # 9 bytes URL safe base64


class RecordSchema(schema.ResourceSchema):
    class Options():
        preserve_unknown = True

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


@record.put(permission=NO_PERMISSION_REQUIRED, schema=RecordSchema)
def record_put(request):
    collection_name = request.matchdict['collection_name']
    record_id = request.matchdict['record_id']
    sync_id = uuid4_to_base64(record_id)

    if_unmodified_since = request.headers.get('If-Match')

    record = request.validated['data']
    record['id'] = sync_id

    sync_client = build_sync_client(request)
    last_modified = sync_client.put_record(collection_name, record,
                                           if_unmodified_since)

    record['last_modified'] = int(last_modified * 1000)
    record['id'] = record_id

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
    del request.response.headers['Content-Type']
    return request.response
