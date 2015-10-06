try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

import webtest
from cliquet.tests import support as cliquet_support
from syncto import main as testapp


ENCRYPTED_CREDENTIALS = (
    '6d4d20478dd81484aef640931d44787d24fc591382782f3aa724a77346dd4bbc22'
    '6b84e42eaadf7f6baa6f1aefd6b60251abf11c1deb1a8f861b4955ce21c4b9979d'
    '9585ca14e2f2581aa2bc3e80915743dacdb244e5f21a6dd8c054bc8826bbf9ca44'
    '6344e1ccebe7f0c9953aaefd44600e9d21f98fc4cda2ed2c58db890a235ce6cdf8'
    '640de4b2506c5b73fe6617bd2e90de64a01aee89306accae133e45e3e64818c426'
)


class BaseWebTest(object):

    def __init__(self, *args, **kwargs):
        super(BaseWebTest, self).__init__(*args, **kwargs)
        self.app = self._get_test_app()
        self.headers = {
            'Content-Type': 'application/json',
        }

    def _get_test_app(self, settings=None):
        app = webtest.TestApp(testapp({}, **self.get_app_settings(settings)))
        app.RequestClass = cliquet_support.get_request_class(prefix="v1")
        return app

    def get_app_settings(self, additional_settings=None):
        settings = cliquet_support.DEFAULT_SETTINGS.copy()
        settings['cache_backend'] = 'cliquet.cache.memory'
        settings['userid_hmac_secret'] = "this is not a secret"
        settings['cache_hmac_secret'] = 'This is not a secret'

        if additional_settings is not None:
            settings.update(additional_settings)
        return settings
