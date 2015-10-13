import requests


def ping_sync_cluster(request):
    settings = request.registry.settings
    token_server_url = settings['token_server_url']
    timeout = settings['token_server_heartbeat_timeout_seconds']
    resp = requests.get('%s/__heartbeat__' % token_server_url.rstrip('/'),
                        timeout=timeout)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        return False
    else:
        return True
