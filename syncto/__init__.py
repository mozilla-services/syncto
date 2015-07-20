import pkg_resources

import cliquet
from pyramid.config import Configurator

# Module version, as defined in PEP-0396.
__version__ = pkg_resources.get_distribution(__package__).version


def main(global_config, **settings):
    config = Configurator(settings=settings)

    cliquet.initialize(config, __version__)
    config.scan("syncto.views")
    return config.make_wsgi_app()
