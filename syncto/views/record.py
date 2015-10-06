import re

import colander
from cliquet import Service, schema, errors
from pyramid import httpexceptions
from pyramid.security import NO_PERMISSION_REQUIRED

from syncto.authentication import build_sync_client
from syncto.headers import import_headers, export_headers


SYNC_ID_FORMAT = re.compile(r'^[a-zA-Z0-9_-]{12}$')  # 9 bytes URL safe base64


class RecordSchema(schema.ResourceSchema):
    class Options():
        preserve_unknown = True


class PayloadSchema(colander.MappingSchema):
    data = RecordSchema()

    def schema_type(self, **kw):
        return colander.Mapping(unknown='raise')


def assert_endpoint_enabled(request, collection_name):
    """Check that endpoint is not disabled from configuration.
    """
    settings = request.registry.settings
    method = request.method.lower()
    setting_key = 'record_%s_%s_enabled' % (collection_name, method)
    enabled = settings.get(setting_key, False)
    if not enabled:
        error_msg = 'Endpoint disabled for this collection in configuration.'
        response = errors.http_error(httpexceptions.HTTPMethodNotAllowed(),
                                     errno=errors.ERRORS.METHOD_NOT_ALLOWED,
                                     message=error_msg)
        raise response


record = Service(name='record',
                 description='Firefox Sync Collection Record service',
                 path=('/buckets/syncto/collections/'
                       '{collection_name}/records/{record_id}'),
                 cors_headers=('Last-Modified', 'ETag'))


@record.get(permission=NO_PERMISSION_REQUIRED)
def record_get(request):
    collection_name = request.matchdict['collection_name']
    record_id = request.matchdict['record_id']

    sync_client = build_sync_client(request)
    headers = import_headers(request)
    record = sync_client.get_record(collection_name, record_id,
                                    headers=headers)

    record['last_modified'] = int(record.pop('modified') * 1000)

    # Configure headers
    export_headers(sync_client.raw_resp, request)

    return {'data': record}


@record.put(permission=NO_PERMISSION_REQUIRED, schema=PayloadSchema)
def record_put(request):
    collection_name = request.matchdict['collection_name']

    assert_endpoint_enabled(request, collection_name)

    record_id = request.matchdict['record_id']
    sync_id = record_id

    headers = import_headers(request)
    record = request.validated['data']
    record['id'] = sync_id

    sync_client = build_sync_client(request)
    last_modified = sync_client.put_record(collection_name, record,
                                           headers=headers)
    record['last_modified'] = int(last_modified * 1000)
    record['id'] = record_id

    # Configure headers
    export_headers(sync_client.raw_resp, request)

    return {'data': record}


@record.delete(permission=NO_PERMISSION_REQUIRED)
def record_delete(request):
    collection_name = request.matchdict['collection_name']

    assert_endpoint_enabled(request, collection_name)

    record_id = request.matchdict['record_id']
    sync_id = record_id

    headers = import_headers(request)
    sync_client = build_sync_client(request)
    sync_client.delete_record(collection_name, sync_id, headers=headers)

    request.response.status_code = 204
    del request.response.headers['Content-Type']
    return request.response
