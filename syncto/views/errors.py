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

    if context.response.status_code in (400, 401):
            message = '%s %s: %s' % (context.response.status_code,
                                     context.response.reason,
                                     context.response.text)
            response = http_error(httpexceptions.HTTPUnauthorized(),
                                  errno=ERRORS.INVALID_AUTH_TOKEN,
                                  message=message)
            # Forget the current user credentials.
            response.headers.extend(forget(request))
    else:
        response = service_unavailable(context, request)

    return reapply_cors(request, response)
