try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA

import webtest
from cliquet.tests import support as cliquet_support
from syncto import main as testapp


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
        settings['cliquet.cache_backend'] = 'cliquet.cache.memory'
        settings['cliquet.storage_backend'] = 'cliquet.storage.memory'
        settings['cliquet.permission_backend'] = 'cliquet.permission.memory'
        settings['cliquet.userid_hmac_secret'] = "this is not a secret"
        settings['syncto.cache_hmac_secret'] = 'This is not a secret'

        if additional_settings is not None:
            settings.update(additional_settings)
        return settings
