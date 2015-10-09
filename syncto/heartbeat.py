import requests


def get_token_server_ping(token_server_url, timeout=5):
    def ping_sync_cluster(request):
        resp = requests.get('%s/__heartbeat__' % token_server_url.rstrip('/'),
                            timeout=timeout)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            return False
        else:
            return True
    return ping_sync_cluster
