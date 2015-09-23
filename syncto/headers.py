from cliquet import utils


def import_headers(syncto_request, sync_request_headers=None):
    """Convert incoming Kinto headers into Sync headers."""
    request_headers = syncto_request.headers
    headers = sync_request_headers or {}

    if 'If-Match' in request_headers:
        headers['X-If-Unmodified-Since'] = '%.2f' % (
            int(request_headers['If-Match']) / 1000.0)

    if 'If-None-Match' in request_headers:
        if request_headers['If-None-Match'] == '*':
            headers['X-If-Unmodified-Since'] = 0
        else:
            headers['X-If-Modified-Since'] = '%.2f' % (
                int(request_headers['If-None-Match']) / 1000.0)

    return headers


def export_headers(sync_raw_response, current_request):
    """Convert Sync headers to Kinto compatible ones."""
    response_headers = sync_raw_response.headers
    syncto_response = current_request.response
    headers = syncto_response.headers

    if 'X-Last-Modified' in response_headers:
        last_modified = float(response_headers['X-Last-Modified'])
        headers['ETag'] = '"%s"' % int(last_modified * 1000)
        syncto_response.last_modified = last_modified

    if 'X-Weave-Next-Offset' in response_headers:
        params = current_request.GET.copy()
        params['_token'] = str(response_headers['X-Weave-Next-Offset'])
        service = utils.current_service(current_request)
        next_page_url = current_request.route_url(service.name, _query=params,
                                                  **current_request.matchdict)
        headers['Next-Page'] = next_page_url

    if 'X-Weave-Records' in response_headers:
        headers['Total-Records'] = str(response_headers['X-Weave-Records'])

    if 'X-Weave-Quota-Remaining' in response_headers:
        headers['Quota-Remaining'] = str(
            response_headers['X-Weave-Quota-Remaining'])

    if 'X-Weave-Alert' in response_headers:
        headers['Alert'] = str(
            response_headers['X-Weave-Alert'])

    if 'X-Weave-Backoff' in response_headers:
        headers['Backoff'] = str(
            response_headers['X-Weave-Backoff'])
