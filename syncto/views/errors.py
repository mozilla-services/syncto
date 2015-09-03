from pyramid import httpexceptions
from pyramid.security import NO_PERMISSION_REQUIRED, forget
from pyramid.view import view_config
from requests.exceptions import HTTPError

from cliquet import logger
from cliquet.errors import http_error, ERRORS
from cliquet.utils import reapply_cors
from cliquet.views.errors import service_unavailable


@view_config(context=HTTPError, permission=NO_PERMISSION_REQUIRED)
def error(context, request):
    """Catch server errors and trace them."""
    logger.error(context, exc_info=True)

    message = '%s %s: %s' % (context.response.status_code,
                             context.response.reason,
                             context.response.text)
    if context.response.status_code == 400:
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
    else:
        response = service_unavailable(context, request)

    return reapply_cors(request, response)
