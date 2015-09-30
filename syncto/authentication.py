from pyramid import httpexceptions
from pyramid.security import forget

from cliquet.errors import http_error, ERRORS
from cliquet import utils
from syncclient.client import SyncClient, TokenserverClient

from syncto import AUTHORIZATION_HEADER, CLIENT_STATE_HEADER


def build_sync_client(request):
    # Get the BID assertion
    is_authorization_defined = AUTHORIZATION_HEADER in request.headers
    starts_with_browser_id = False
    if is_authorization_defined:
        authorization = request.headers[AUTHORIZATION_HEADER].lower()
        starts_with_browser_id = authorization.startswith("browserid ")

    if not is_authorization_defined or not starts_with_browser_id:
        msg = "Provide a BID assertion %s header." % AUTHORIZATION_HEADER
        response = http_error(httpexceptions.HTTPUnauthorized(),
                              errno=ERRORS.MISSING_AUTH_TOKEN,
                              message=msg)
        response.headers.extend(forget(request))
        raise response

    is_client_state_defined = CLIENT_STATE_HEADER in request.headers
    if not is_client_state_defined:
        msg = "Provide the tokenserver %s header." % CLIENT_STATE_HEADER
        response = http_error(httpexceptions.HTTPUnauthorized(),
                              errno=ERRORS.MISSING_AUTH_TOKEN,
                              message=msg)
        response.headers.extend(forget(request))
        raise response

    authorization_header = request.headers[AUTHORIZATION_HEADER]
    bid_assertion = authorization_header.split(" ", 1)[1]
    client_state = request.headers[CLIENT_STATE_HEADER]

    settings = request.registry.settings
    cache = request.registry.cache
    statsd = request.registry.statsd

    hmac_secret = settings['syncto.cache_hmac_secret']
    cache_key = 'credentials_%s' % utils.hmac_digest(hmac_secret,
                                                     bid_assertion)

    credentials = cache.get(cache_key)

    if not credentials:
        ttl = int(settings['syncto.cache_credentials_ttl_seconds'])
        tokenserver = TokenserverClient(bid_assertion, client_state)
        if statsd:
            statsd.watch_execution_time(tokenserver, prefix="tokenserver")
        credentials = tokenserver.get_hawk_credentials(duration=ttl)
        cache.set(cache_key, credentials, ttl)

    if statsd:
        timer = statsd.timer("syncclient.start_time")
        timer.start()

    sync_client = SyncClient(**credentials)

    if statsd:
        timer.stop()
        statsd.watch_execution_time(sync_client, prefix="syncclient")

    return sync_client
