import pkg_resources

import cliquet
from pyramid.config import Configurator

# Module version, as defined in PEP-0396.
__version__ = pkg_resources.get_distribution(__package__).version

try:
    # Verify that we are using the Py2 urllib3 version with OpenSSL installed
    from requests.packages.urllib3.contrib import pyopenssl
except ImportError:  # Pragma: no cover
    pass
else:
    pyopenssl.inject_into_urllib3()  # Pragma: no cover

AUTHORIZATION_HEADER = 'Authorization'
CLIENT_STATE_HEADER = 'X-Client-State'

DEFAULT_SETTINGS = {
    'project_name': 'syncto',
    'project_docs': 'https://syncto.readthedocs.org/',
    'cache_hmac_secret': None,
    'cache_credentials_ttl_seconds': 300
}


def main(global_config, **settings):
    config = Configurator(settings=settings)

    cliquet.initialize(config, __version__, 'syncto',
                       default_settings=DEFAULT_SETTINGS)

    settings = config.get_settings()

    if settings['cache_hmac_secret'] is None:
        error_msg = "Please configure the `syncto.cache_hmac_secret` settings."
        raise ValueError(error_msg)

    config.scan("syncto.views")
    return config.make_wsgi_app()
