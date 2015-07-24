import pkg_resources

import cliquet
from pyramid.config import Configurator

# Module version, as defined in PEP-0396.
__version__ = pkg_resources.get_distribution(__package__).version

try:
    # Verify that we are using the Py2 urllib3 version with OpenSSL installed
    from requests.packages.urllib3.contrib import pyopenssl
except ImportError:
    pass
else:
    pyopenssl.inject_into_urllib3()

AUTHORIZATION_HEADER = 'Authorization'
CLIENT_STATE_HEADER = 'X-Client-State'


def main(global_config, **settings):
    config = Configurator(settings=settings)

    cliquet.initialize(config, __version__)
    config.scan("syncto.views")
    return config.make_wsgi_app()
