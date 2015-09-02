def convert_headers(sync_raw_response, syncto_response):
    """Convert Sync headers to Kinto compatible ones."""
    response_headers = sync_raw_response.headers
    headers = syncto_response.headers

    last_modified = float(response_headers['X-Last-Modified'])
    headers['ETag'] = '"%s"' % int(last_modified * 1000)
    syncto_response.last_modified = last_modified

    if 'X-Weave-Next-Offset' in response_headers:
        headers['Next-Page'] = str(response_headers['X-Weave-Next-Offset'])

    if 'X-Weave-Records':
        headers['Total-Records'] = str(response_headers['X-Weave-Records'])
