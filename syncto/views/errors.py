from pyramid import httpexceptions
from pyramid.security import NO_PERMISSION_REQUIRED, forget
from pyramid.view import view_config
from requests.exceptions import HTTPError, RequestException

from cliquet import logger
from cliquet.errors import http_error, ERRORS
from cliquet.utils import reapply_cors
from cliquet.views.errors import service_unavailable

from syncto.headers import export_headers


@view_config(context=HTTPError, permission=NO_PERMISSION_REQUIRED)
def response_error(context, request):
    """Catch response error from Sync and trace them."""
    message = '%s %s: %s' % (context.response.status_code,
                             context.response.reason,
                             context.response.text)

    statsd = request.registry.statsd

    if statsd:
        statsd.count("syncclient.status_code.%s" %
                     context.response.status_code)

    if context.response.status_code in (400, 401, 403, 404):
        # For this code we also want to log the info about the error.
        logger.info(context, exc_info=True)

    # For this specific code we do not want to log the error.
    if context.response.status_code == 304:
        response = httpexceptions.HTTPNotModified()
    elif context.response.status_code == 400:
        response = http_error(httpexceptions.HTTPBadRequest(),
                              errno=ERRORS.INVALID_PARAMETERS,
                              message=message)
    elif context.response.status_code == 401:
        response = http_error(httpexceptions.HTTPUnauthorized(),
                              errno=ERRORS.INVALID_AUTH_TOKEN,
                              message=message)
        # Forget the current user credentials.
        response.headers.extend(forget(request))
    elif context.response.status_code == 403:
        response = http_error(httpexceptions.HTTPForbidden(),
                              errno=ERRORS.FORBIDDEN,
                              message=message)
    elif context.response.status_code == 404:
        response = http_error(httpexceptions.HTTPNotFound(),
                              errno=ERRORS.INVALID_RESOURCE_ID,
                              message=message)
    elif context.response.status_code == 412:
        message = 'Resource was modified meanwhile'
        response = http_error(httpexceptions.HTTPPreconditionFailed(),
                              errno=ERRORS.MODIFIED_MEANWHILE,
                              message=message)
    else:
        # For this code we also want to log the error.
        logger.error(context, exc_info=True)
        response = service_unavailable(
            httpexceptions.HTTPServiceUnavailable(),
            request)

    request.response = response
    export_headers(context.response, request)

    return reapply_cors(request, response)


@view_config(context=RequestException, permission=NO_PERMISSION_REQUIRED)
def request_error(context, request):
    """Catch requests errors when issuing a request to Sync."""
    logger.error(context, exc_info=True)

    error_msg = ("Unable to reach the service. "
                 "Check your internet connection or firewall configuration.")
    response = http_error(httpexceptions.HTTPServiceUnavailable(),
                          errno=ERRORS.BACKEND,
                          message=error_msg)

    return service_unavailable(response, request)
